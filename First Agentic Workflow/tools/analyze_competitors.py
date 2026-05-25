#!/usr/bin/env python3
"""
Synthesizes all per-competitor research + business profile into actionable insights using Claude.
Usage: python tools/analyze_competitors.py --profile config/business_profile.json --research-dir .tmp/
Output: JSON written to .tmp/analysis.json and printed to stdout.
"""

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
TMP_DIR = ROOT / ".tmp"

load_dotenv(ROOT / ".env")


def extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser(description="Synthesize competitor analysis with Claude")
    parser.add_argument("--profile", default="config/business_profile.json")
    parser.add_argument("--research-dir", default=".tmp")
    parser.add_argument("--output", default=".tmp/analysis.json")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY not found in .env")

    profile_path = ROOT / args.profile
    if not profile_path.exists():
        sys.exit(f"Error: profile not found at {profile_path}")

    profile = json.loads(profile_path.read_text())

    research_dir = ROOT / args.research_dir
    research_files = sorted(research_dir.glob("research_*.json"))
    if not research_files:
        sys.exit(f"Error: no research_*.json files found in {research_dir}. Run research_competitor.py first.")

    competitors = []
    for f in research_files:
        try:
            competitors.append(json.loads(f.read_text()))
        except Exception as e:
            print(f"  Warning: could not load {f.name}: {e}", file=sys.stderr)

    print(f"Analyzing {len(competitors)} competitors against {profile['business_name']}...", file=sys.stderr)

    competitor_block = json.dumps(competitors, indent=2)
    profile_block = json.dumps(profile, indent=2)

    prompt = f"""You are a senior business strategist conducting a competitive analysis for {profile['business_name']}.

YOUR BUSINESS:
{profile_block}

COMPETITOR RESEARCH:
{competitor_block}

Your task: synthesize all of this into a rigorous, specific, and actionable competitive analysis.
Be direct and concrete — avoid generic statements. Every insight should be specific to {profile['business_name']} and the actual research data.

Return a JSON object with EXACTLY these keys:

{{
  "executive_summary": "3-5 sentence summary of the competitive landscape and {profile['business_name']}'s position. Be specific.",

  "market_landscape": "2-3 paragraphs describing how this market is structured, who the main players are, and what the key competitive dynamics are.",

  "competitor_profiles": [
    {{
      "name": "competitor name",
      "one_liner": "what they do in one sentence",
      "threat_level": "high / medium / low",
      "threat_reasoning": "why this threat level — specific to {profile['business_name']}"
    }}
  ],

  "what_competitors_do_well": [
    {{
      "theme": "e.g. Pricing transparency",
      "detail": "specific observation with competitor names",
      "implication_for_us": "what this means for {profile['business_name']}"
    }}
  ],

  "gaps_and_opportunities": [
    {{
      "opportunity": "specific gap in the market",
      "evidence": "which competitors are missing this, and how",
      "priority": "high / medium / low",
      "suggested_action": "concrete thing {profile['business_name']} could do"
    }}
  ],

  "threats": [
    {{
      "threat": "specific threat description",
      "source": "which competitor(s) pose this threat",
      "urgency": "immediate / near-term / watch"
    }}
  ],

  "recommendations": [
    {{
      "recommendation": "specific, actionable recommendation",
      "rationale": "why — tied to specific competitive evidence",
      "effort": "quick win / medium effort / strategic initiative"
    }}
  ],

  "generated_at": "{date.today().isoformat()}"
}}

Return ONLY valid JSON. No markdown fences, no explanation."""

    claude = anthropic.Anthropic(api_key=api_key)

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text

    try:
        analysis = extract_json(raw)
    except Exception:
        print("  JSON parse failed, asking Claude to repair...", file=sys.stderr)
        repair = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": f"Fix this JSON so it parses correctly. Return only valid JSON:\n{raw}"}]
        )
        analysis = extract_json(repair.content[0].text)

    out_path = ROOT / args.output
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(analysis, indent=2))
    print(f"Analysis saved to {out_path}", file=sys.stderr)

    print("\n--- EXECUTIVE SUMMARY ---", file=sys.stderr)
    print(analysis.get("executive_summary", ""), file=sys.stderr)
    print(f"\nOpportunities found: {len(analysis.get('gaps_and_opportunities', []))}", file=sys.stderr)
    print(f"Threats identified:  {len(analysis.get('threats', []))}", file=sys.stderr)
    print(f"Recommendations:     {len(analysis.get('recommendations', []))}", file=sys.stderr)

    print(json.dumps(analysis))


if __name__ == "__main__":
    main()
