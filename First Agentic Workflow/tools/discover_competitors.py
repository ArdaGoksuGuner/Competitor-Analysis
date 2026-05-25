#!/usr/bin/env python3
"""
Discovers competitors using Tavily web search + Claude deduplication.
Usage: python tools/discover_competitors.py --profile config/business_profile.json
Output: JSON list written to .tmp/competitors.json and printed to stdout.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"

load_dotenv(ROOT / ".env")


def extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def search(client: TavilyClient, query: str) -> list[dict]:
    try:
        result = client.search(query=query, search_depth="advanced", max_results=8)
        return result.get("results", [])
    except Exception as e:
        print(f"  Search warning ({query[:50]}...): {e}", file=sys.stderr)
        return []


def main():
    parser = argparse.ArgumentParser(description="Auto-discover competitors via Tavily")
    parser.add_argument("--profile", default="config/business_profile.json")
    parser.add_argument("--num-competitors", type=int, default=5)
    args = parser.parse_args()

    tavily_key = os.getenv("TAVILY_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not tavily_key:
        sys.exit("Error: TAVILY_API_KEY not found in .env")
    if not anthropic_key:
        sys.exit("Error: ANTHROPIC_API_KEY not found in .env")

    profile_path = ROOT / args.profile
    if not profile_path.exists():
        sys.exit(f"Error: profile not found at {profile_path}. Run setup_profile.py first.")

    profile = json.loads(profile_path.read_text())
    biz = profile["business_name"]
    industry = profile.get("industry", "")
    description = profile.get("description", "")
    target = profile.get("target_market", "")
    products = ", ".join(profile.get("key_products_services", []))

    print(f"Discovering competitors for: {biz} ({industry})", file=sys.stderr)

    tavily = TavilyClient(api_key=tavily_key)
    claude = anthropic.Anthropic(api_key=anthropic_key)

    queries = [
        f"top competitors of {biz} in {industry}",
        f"best alternatives to {biz} {industry} {target}",
        f"leading companies in {industry} similar to {biz}",
        f"{industry} market leaders {products}",
    ]

    all_results = []
    for i, q in enumerate(queries):
        print(f"  Searching: {q}", file=sys.stderr)
        all_results.extend(search(tavily, q))
        if i < len(queries) - 1:
            time.sleep(0.5)

    raw_text = "\n\n".join(
        f"Title: {r.get('title', '')}\nURL: {r.get('url', '')}\nSnippet: {r.get('content', '')}"
        for r in all_results
    )

    known = profile.get("known_competitors", [])
    known_note = f"\nAlso always include these known competitors: {', '.join(known)}" if known else ""

    prompt = f"""You are analyzing web search results to identify competitors for a business.

Business: {biz}
Industry: {industry}
Description: {description}
Target market: {target}
Products/services: {products}{known_note}

Search results:
{raw_text}

Extract exactly {args.num_competitors} distinct competitors. For each, provide:
- name: company name
- url: their main website URL (best guess if not explicitly found)
- description: one sentence on what they do and why they compete with {biz}

Return ONLY a JSON array. No explanation, no markdown fences.
Example: [{{"name":"...", "url":"...", "description":"..."}}]"""

    print("Asking Claude to extract competitor list...", file=sys.stderr)
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text

    try:
        competitors = extract_json(raw)
    except Exception:
        repair_prompt = f"The following text should be a JSON array but failed to parse. Return only valid JSON:\n{raw}"
        repair = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": repair_prompt}]
        )
        competitors = extract_json(repair.content[0].text)

    TMP_DIR.mkdir(exist_ok=True)
    out_path = TMP_DIR / "competitors.json"
    out_path.write_text(json.dumps(competitors, indent=2))

    print(f"Found {len(competitors)} competitors:", file=sys.stderr)
    for c in competitors:
        print(f"  - {c['name']} ({c.get('url', 'URL unknown')})", file=sys.stderr)

    print(json.dumps(competitors))


if __name__ == "__main__":
    main()
