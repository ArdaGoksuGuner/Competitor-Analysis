# Competitor Analysis — WAT Framework

An AI-powered competitive intelligence system that researches competitors, synthesizes strategic insights, and produces a branded PDF report — fully automated and runnable on demand.

Built on the **WAT framework** (Workflows · Agents · Tools): deterministic Python scripts handle execution, Claude handles reasoning.

---

## What it does

1. **Discovers** the top competitors for your business using web search
2. **Researches** each competitor across 5 dimensions: products & pricing, recent news, marketing positioning, customer sentiment, and company signals
3. **Synthesizes** a strategic analysis with opportunities, threats, and recommendations
4. **Generates** a branded PDF report ready to share

A full run takes **5–15 minutes** and produces a report like this:

| Section | What's inside |
|---|---|
| Executive Summary | Competitive landscape in 3–5 sentences |
| Market Landscape | How the market is structured and who the players are |
| Competitor Profiles | Threat-level cards for each competitor |
| What Competitors Do Well | Themes with implications for your business |
| Gaps & Opportunities | Specific gaps with priority levels and suggested actions |
| Threats to Watch | Immediate, near-term, and watch-list threats |
| Recommendations | Actionable steps tied to competitive evidence |

---

## Architecture

```
workflows/          # Markdown SOPs — what to do and how
tools/              # Python scripts — deterministic execution
config/             # Business profile and brand settings
reports/            # Generated PDF reports (output)
.tmp/               # Intermediate files (regenerated each run)
```

**Tools:**

| Script | What it does |
|---|---|
| `setup_profile.py` | Interactive setup for business profile and brand config |
| `discover_competitors.py` | Uses Tavily search + Claude to find top competitors |
| `research_competitor.py` | Deep-dives a single competitor across 5 search angles |
| `analyze_competitors.py` | Synthesizes all research into structured strategic analysis |
| `generate_pdf.py` | Renders a branded PDF report from the analysis |

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/ArdaGoksuGuner/Competitor-Analysis.git
cd Competitor-Analysis
pip install -r requirements.txt
```

> On macOS, WeasyPrint requires Pango. Install via Homebrew:
> ```bash
> brew install pango
> ```

**2. Add API keys**

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Get your keys at [console.anthropic.com](https://console.anthropic.com) and [tavily.com](https://tavily.com).

**3. Set up your business profile**

```bash
python tools/setup_profile.py --interactive
```

This creates `config/business_profile.json` and `config/brand.json`.

---

## Running a competitor analysis

**Step 1 — Discover competitors**

```bash
python tools/discover_competitors.py --profile config/business_profile.json --num-competitors 5
```

Review the list. Edit `.tmp/competitors.json` if you want to swap any out.

**Step 2 — Research each competitor**

Run sequentially (one at a time) to avoid rate limits:

```bash
python tools/research_competitor.py \
  --name "Competitor Name" \
  --url "https://competitor.com" \
  --output ".tmp/research_competitorname.json"
```

**Step 3 — Synthesize the analysis**

```bash
python tools/analyze_competitors.py \
  --profile config/business_profile.json \
  --research-dir .tmp \
  --output .tmp/analysis.json
```

**Step 4 — Generate the PDF**

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3.11 tools/generate_pdf.py \
  --analysis .tmp/analysis.json \
  --brand config/brand.json \
  --profile config/business_profile.json
```

Output: `reports/competitor_analysis_YYYY-MM-DD.pdf`

---

## Requirements

- Python 3.11+
- [Anthropic API key](https://console.anthropic.com) (Claude Sonnet)
- [Tavily API key](https://tavily.com) (web search)
- macOS/Linux with Pango installed (for PDF generation)

---

## How the WAT framework works

Most AI agents fail at multi-step tasks because accuracy compounds downward — 5 steps at 90% accuracy each gives you 59% success. This system avoids that by separating concerns:

- **Workflows** define the objective, steps, and edge cases in plain language
- **The Agent** (Claude) reads the workflow and orchestrates execution
- **Tools** are Python scripts that do the actual work — API calls, file operations, data transformations

The agent reasons. The tools execute. That separation is what makes it reliable.
