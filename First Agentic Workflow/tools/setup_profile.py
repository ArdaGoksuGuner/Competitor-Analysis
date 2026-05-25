#!/usr/bin/env python3
"""
One-time setup: saves business profile and writes Lumen brand config.
Run: python tools/setup_profile.py --interactive
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONFIG_DIR = ROOT / "config"

LUMEN_BRAND = {
    "name": "Lumen",
    "tagline": "LEARN · ILLUMINATE · GROW",
    "logo_path": "config/logo.png",
    "colors": {
        "primary": "#D24B2D",
        "secondary": "#691E1E",
        "accent": "#E1961E",
        "light_accent": "#F0B45A",
        "background": "#F5EDE0",
        "body_text": "#2D2D2D",
        "label_text": "#535476"
    },
    "fonts": {
        "primary": "Arial",
        "accent": "Georgia"
    }
}


def prompt(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    value = input(f"{label}{hint}: ").strip()
    return value if value else default


def run_interactive():
    print("\n=== Lumen Business Profile Setup ===\n")

    business_name = prompt("Business name", "Lumen")
    website = prompt("Website URL (e.g. https://yourbusiness.com)")
    industry = prompt("Industry (e.g. EdTech, SaaS, E-commerce)")
    description = prompt("One-sentence description of what your business does")
    target_market = prompt("Target market (e.g. 'small business owners', 'students aged 18-25')")

    print("\nKey products/services (press Enter after each, blank line to finish):")
    products = []
    while True:
        item = input("  > ").strip()
        if not item:
            break
        products.append(item)

    print("\nKnown competitors to always include (optional, blank line to skip):")
    known_competitors = []
    while True:
        item = input("  > ").strip()
        if not item:
            break
        known_competitors.append(item)

    profile = {
        "business_name": business_name,
        "website": website,
        "industry": industry,
        "description": description,
        "target_market": target_market,
        "key_products_services": products,
        "known_competitors": known_competitors
    }

    CONFIG_DIR.mkdir(exist_ok=True)

    profile_path = CONFIG_DIR / "business_profile.json"
    profile_path.write_text(json.dumps(profile, indent=2))
    print(f"\n✓ Business profile saved to {profile_path}")

    brand_path = CONFIG_DIR / "brand.json"
    brand_path.write_text(json.dumps(LUMEN_BRAND, indent=2))
    print(f"✓ Lumen brand config saved to {brand_path}")

    logo_src = ROOT / "Lumen.png"
    logo_dst = CONFIG_DIR / "logo.png"
    if logo_src.exists():
        shutil.copy2(logo_src, logo_dst)
        print(f"✓ Logo copied to {logo_dst}")
    else:
        print(f"  Warning: Lumen.png not found at {logo_src} — logo will be missing from PDF")

    print("\n=== Setup complete ===")
    print(f"  Business: {business_name}")
    print(f"  Industry: {industry}")
    print(f"  Products: {', '.join(products) or 'none specified'}")
    print(f"  Known competitors: {', '.join(known_competitors) or 'none — will auto-discover'}")
    print("\nYou're ready to run the competitor analysis workflow.\n")


def main():
    parser = argparse.ArgumentParser(description="Set up Lumen business profile")
    parser.add_argument("--interactive", action="store_true", default=True,
                        help="Prompt for business info interactively (default)")
    args = parser.parse_args()

    if args.interactive:
        run_interactive()
    else:
        print("Use --interactive to run setup.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
