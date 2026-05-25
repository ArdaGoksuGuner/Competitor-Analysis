#!/usr/bin/env python3
"""
Deep-researches a single competitor across 5 dimensions using Tavily + Claude.
Usage: python tools/research_competitor.py --name "Competitor" --url "https://..." --output .tmp/research_competitor.json
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
load_dotenv(ROOT / ".env")


def slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug[:50]


def extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def search(client: TavilyClient, query: str) -> str:
    try:
        result = client.search(query=query, search_depth="advanced", max_results=6)
        results = result.get("results", [])
        return "\n\n".join(
            f"[{r.get('title', '')}] {r.get('url', '')}\n{r.get('content', '')}"
            for r in results
        )
    except Exception as e:
        print(f"  Search warning: {e}", file=sys.stderr)
        return ""


def main():
    parser = argparse.ArgumentParser(description="Deep-research a single competitor")
    parser.add_argument("--name", required=True, help="Competitor name")
    parser.add_argument("--url", required=True, help="Competitor website URL")
    parser.add_argument("--output", help="Output JSON file path (auto-generated if omitted)")
    args = parser.parse_args()

    tavily_key = os.getenv("TAVILY_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not tavily_key:
        sys.exit("Error: TAVILY_API_KEY not found in .env")
    if not anthropic_key:
        sys.exit("Error: ANTHROPIC_API_KEY not found in .env")

    out_path = Path(args.output) if args.output else ROOT / ".tmp" / f"research_{slugify(args.name)}.json"
    out_path.parent.mkdir(exist_ok=True)

    tavily = TavilyClient(api_key=tavily_key)
    claude = anthropic.Anthropic(api_key=anthropic_key)

    name = args.name
    url = args.url
    print(f"Researching: {name} ({url})", file=sys.stderr)

    dimensions = [
        ("products_pricing", f"{name} products services pricing plans {url}"),
        ("recent_news", f"{name} news announcements launches 2024 2025"),
        ("marketing_positioning", f"{name} marketing messaging brand positioning value proposition"),
        ("customer_sentiment", f"{name} reviews complaints customer feedback pros cons"),
        ("company_signals", f"{name} company size employees funding growth revenue"),
    ]

    raw_research = {}
    for dim_key, query in dimensions:
        print(f"  [{dim_key}] {query}", file=sys.stderr)
        raw_research[dim_key] = search(tavily, query)
        time.sleep(0.5)

    combined = "\n\n---\n\n".join(
        f"=== {key.upper()} ===\n{content}"
        for key, content in raw_research.items()
        if content
    )

    prompt = f"""You are a business analyst. Structure the following research about {name} ({url}) into clean JSON.

Research data:
{combined}

Return a JSON object with EXACTLY these keys:
{{
  "name": "{name}",
  "url": "{url}",
  "products_and_pricing": {{
    "summary": "2-3 sentences on what they offer",
    "key_products": ["product 1", "product 2"],
    "pricing_model": "e.g. subscription, freemium, per-seat, one-time"
  }},
  "recent_developments": ["bullet 1", "bullet 2", "bullet 3"],
  "marketing_positioning": {{
    "core_message": "their main value prop in one sentence",
    "tone": "e.g. professional, playful, authoritative",
    "key_differentiators": ["differentiator 1", "differentiator 2"]
  }},
  "customer_sentiment": {{
    "overall": "positive / mixed / negative",
    "strengths_praised": ["thing 1", "thing 2"],
    "common_complaints": ["complaint 1", "complaint 2"]
  }},
  "company_signals": {{
    "estimated_size": "e.g. startup, mid-size, enterprise",
    "growth_trajectory": "e.g. rapid growth, stable, declining",
    "notable_facts": ["fact 1", "fact 2"]
  }}
}}

Use only information from the research. Write "unknown" where data is missing. Return ONLY valid JSON."""

    print("  Structuring research with Claude...", file=sys.stderr)
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text

    try:
        data = extract_json(raw)
    except Exception:
        repair = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"Fix this JSON so it parses correctly. Return only valid JSON:\n{raw}"}]
        )
        data = extract_json(repair.content[0].text)

    out_path.write_text(json.dumps(data, indent=2))
    print(f"  Saved to {out_path}", file=sys.stderr)
    print(json.dumps(data))


if __name__ == "__main__":
    main()
