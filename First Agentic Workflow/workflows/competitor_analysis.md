# Competitor Analysis Workflow

## Objective
Produce a branded Lumen PDF report that maps the competitive landscape, identifies threats and opportunities, and gives actionable recommendations — so the business can make informed strategic decisions.

## When to Run
On demand, whenever you want a fresh competitive snapshot. Takes 5–15 minutes depending on the number of competitors researched.

---

## Prerequisites

Before running, confirm:
- [ ] `.env` exists with `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
- [ ] `config/business_profile.json` exists (if not, run `python tools/setup_profile.py --interactive` first)
- [ ] `config/brand.json` and `config/logo.png` exist (created automatically by setup)
- [ ] Dependencies installed: `pip install -r requirements.txt`

---

## Step-by-Step

### Step 1 — Discover competitors

```bash
python tools/discover_competitors.py --profile config/business_profile.json --num-competitors 5
```

**Output:** `.tmp/competitors.json` — a list of `{name, url, description}` objects.

**What to do:**
- Read the list back to the user: "I found these 5 competitors: [list them]"
- Ask: "Would you like to add, remove, or swap any before I research them?"
- If the user wants changes, edit `.tmp/competitors.json` directly before proceeding
- If Tavily returns a rate limit error, wait 10 seconds and retry once

---

### Step 2 — Research each competitor

For each competitor in `.tmp/competitors.json`, run:

```bash
python tools/research_competitor.py \
  --name "Competitor Name" \
  --url "https://competitor.com" \
  --output ".tmp/research_competitorname.json"
```

**Output:** One `.tmp/research_<slug>.json` file per competitor.

**Notes:**
- Run these sequentially (not in parallel) to avoid Tavily rate limits
- If a competitor has no meaningful web presence (very sparse results), note it in the report as "limited public information available" and continue — don't skip it entirely
- Each call takes ~30–60 seconds (5 searches + Claude structuring)

---

### Step 3 — Synthesize analysis

```bash
python tools/analyze_competitors.py \
  --profile config/business_profile.json \
  --research-dir .tmp \
  --output .tmp/analysis.json
```

**Output:** `.tmp/analysis.json` — structured analysis with executive summary, opportunities, threats, and recommendations.

**What to do after:**
- Show the user the executive summary (printed to stderr during the run)
- Show the count of opportunities, threats, and recommendations
- Ask: "Does this look right? Want me to regenerate any section?"
- If the output feels generic or off, re-run with a note — re-runs are free (Claude only)

---

### Step 4 — Generate PDF

```bash
python tools/generate_pdf.py \
  --analysis .tmp/analysis.json \
  --brand config/brand.json \
  --profile config/business_profile.json
```

**Output:** `reports/competitor_analysis_YYYY-MM-DD.pdf`

Tell the user the exact file path when done.

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `TAVILY_API_KEY not found` | `.env` missing or wrong key name | Copy `.env.example` → `.env`, fill in the key |
| `ANTHROPIC_API_KEY not found` | Same as above | Same fix |
| `profile not found` | setup not run | Run `python tools/setup_profile.py --interactive` |
| Tavily rate limit (429) | Too many searches too fast | Wait 10s, retry. If persistent, add `time.sleep(1)` between searches |
| `no research_*.json files found` | Step 2 skipped or failed | Re-run Step 2 for each competitor |
| WeasyPrint `OSError` (font) | Font not found on system | Arial is a system font on Mac/Windows; on Linux install `ttf-mscorefonts-installer` |
| PDF is blank / missing logo | Logo path wrong | Check `config/logo.png` exists; re-run setup if needed |

---

## Self-Improvement Notes

- If Tavily consistently returns low-quality results for a specific industry, add more targeted queries to `discover_competitors.py` (lines ~45–50) and document here
- If Claude's analysis feels too surface-level, tighten the prompt in `analyze_competitors.py` — add a line like "If a recommendation would apply to any business, it is too generic. Discard it."
- If WeasyPrint's CSS rendering differs from expectations, test HTML output first: add `--html-only` flag or write `html_content` to `.tmp/report_preview.html` for inspection

---

## Output

Final PDF: `reports/competitor_analysis_YYYY-MM-DD.pdf`

Sections in the PDF:
1. Cover page (Lumen branded, cream background)
2. Executive Summary
3. Market Landscape
4. Competitor Profiles (threat-level cards)
5. What Competitors Do Well
6. Gaps & Opportunities
7. Threats to Watch
8. Recommendations
