#!/usr/bin/env python3
"""
Renders a branded Lumen PDF from the analysis JSON using Jinja2 + WeasyPrint.
Usage: python tools/generate_pdf.py --analysis .tmp/analysis.json --brand config/brand.json
Output: reports/competitor_analysis_YYYY-MM-DD.pdf
"""

import argparse
import base64
import json
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = ROOT / "templates"
REPORTS_DIR = ROOT / "reports"


def b64_image(path: Path) -> str:
    if not path.exists():
        print(f"Warning: logo not found at {path}", file=sys.stderr)
        return ""
    return base64.b64encode(path.read_bytes()).decode("ascii")


def main():
    parser = argparse.ArgumentParser(description="Generate branded Lumen PDF report")
    parser.add_argument("--analysis", default=".tmp/analysis.json")
    parser.add_argument("--brand", default="config/brand.json")
    parser.add_argument("--profile", default="config/business_profile.json")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    analysis_path = ROOT / args.analysis
    brand_path = ROOT / args.brand
    profile_path = ROOT / args.profile

    for p, label in [(analysis_path, "analysis"), (brand_path, "brand"), (profile_path, "profile")]:
        if not p.exists():
            sys.exit(f"Error: {label} file not found at {p}")

    analysis = json.loads(analysis_path.read_text())
    brand = json.loads(brand_path.read_text())
    profile = json.loads(profile_path.read_text())

    logo_path = ROOT / brand.get("logo_path", "config/logo.png")
    logo_b64 = b64_image(logo_path)

    generated_at = analysis.get("generated_at", date.today().isoformat())
    competitors = analysis.get("competitor_profiles", [])

    out_filename = args.output or f"competitor_analysis_{generated_at}.pdf"
    if not out_filename.endswith(".pdf"):
        out_filename += ".pdf"
    REPORTS_DIR.mkdir(exist_ok=True)
    out_path = ROOT / "reports" / Path(out_filename).name

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")

    html_content = template.render(
        analysis=analysis,
        brand=brand,
        profile=profile,
        logo_b64=logo_b64,
        generated_at=generated_at,
        competitors=competitors,
    )

    print(f"Rendering PDF...", file=sys.stderr)
    HTML(string=html_content, base_url=str(ROOT)).write_pdf(str(out_path))

    print(f"PDF saved: {out_path}", file=sys.stderr)
    print(str(out_path))


if __name__ == "__main__":
    main()
