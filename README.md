# Competitor Analysis — WAT Framework

An AI-powered competitive intelligence system that researches competitors, synthesizes strategic insights, and produces a **branded PDF report tailored to your company** — fully automated and runnable on demand.

You configure it once with your business profile and brand guidelines. It discovers your competitors, researches them in depth, and delivers a polished strategic report specific to your business — not a generic template.

Built on the **WAT framework** (Workflows · Agents · Tools): deterministic Python scripts handle execution, Claude handles reasoning.

---

## What it produces

A branded PDF report with 7 sections, specific to your company:

| Section | What's inside |
|---|---|
| Executive Summary | Your competitive position in 3–5 sentences |
| Market Landscape | How your market is structured and who the key players are |
| Competitor Profiles | Threat-level cards for each competitor |
| What Competitors Do Well | Themes with direct implications for your business |
| Gaps & Opportunities | Specific market gaps, prioritized, with suggested actions |
| Threats to Watch | Immediate, near-term, and watch-list threats |
| Recommendations | Actionable steps tied to competitive evidence |

A full run takes **5–15 minutes** depending on the number of competitors.

---

## Architecture

```
First Agentic Workflow/
├── workflows/      # Markdown SOPs — what to do and how
├── tools/          # Python scripts — deterministic execution
├── config/         # Your business profile and brand settings
├── templates/      # HTML template for the PDF report
├── reports/        # Generated PDF reports (output)
└── .tmp/           # Intermediate files (regenerated each run)
```

**Tools:**

| Script | What it does |
|---|---|
| `setup_profile.py` | One-time interactive setup — enter your business details and brand |
| `discover_competitors.py` | Finds your top competitors using web search + Claude |
| `research_competitor.py` | Deep-dives a single competitor across 5 dimensions |
| `analyze_competitors.py` | Synthesizes all research into a structured strategic analysis |
| `generate_pdf.py` | Renders a branded PDF report from the analysis |

---

## Setup

**1. Clone and install dependencies**

```bash
git clone https://github.com/ArdaGoksuGuner/Competitor-Analysis.git
cd Competitor-Analysis
pip install -r "First Agentic Workflow/requirements.txt"
```

> On macOS, WeasyPrint requires Pango. Install via Homebrew:
> ```bash
> brew install pango
> ```

**2. Add your API keys**

```bash
cp "First Agentic Workflow/.env.example" "First Agentic Workflow/.env"
```

Edit `.env` and fill in:

```
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Get your keys at [console.anthropic.com](https://console.anthropic.com) and [tavily.com](https://tavily.com).

**3. Configure your business profile**

```bash
python "First Agentic Workflow/tools/setup_profile.py" --interactive
```

You'll be prompted for your business name, industry, target market, key offerings, brand colors, and logo. This is what makes every report specific to your company — not a generic analysis.

---

## Running an analysis

**Step 1 — Discover competitors**

```bash
python "First Agentic Workflow/tools/discover_competitors.py" \
  --profile "First Agentic Workflow/config/business_profile.json" \
  --num-competitors 5
```

Review the list. Edit `.tmp/competitors.json` to swap any out before proceeding.

**Step 2 — Research each competitor**

Run sequentially to avoid API rate limits:

```bash
python "First Agentic Workflow/tools/research_competitor.py" \
  --name "Competitor Name" \
  --url "https://competitor.com" \
  --output ".tmp/research_competitorname.json"
```

Repeat for each competitor. Each call runs 5 targeted searches and takes ~30–60 seconds.

**Step 3 — Synthesize the analysis**

```bash
python "First Agentic Workflow/tools/analyze_competitors.py" \
  --profile "First Agentic Workflow/config/business_profile.json" \
  --research-dir .tmp \
  --output .tmp/analysis.json
```

**Step 4 — Generate the PDF**

```bash
DYLD_LIBRARY_PATH=/opt/homebrew/lib python3.11 "First Agentic Workflow/tools/generate_pdf.py" \
  --analysis .tmp/analysis.json \
  --brand "First Agentic Workflow/config/brand.json" \
  --profile "First Agentic Workflow/config/business_profile.json"
```

Output: `First Agentic Workflow/reports/competitor_analysis_YYYY-MM-DD.pdf`

---

## Requirements

- Python 3.11+
- [Anthropic API key](https://console.anthropic.com) — Claude Sonnet for reasoning and synthesis
- [Tavily API key](https://tavily.com) — web search for competitor research
- macOS/Linux with Pango installed (for PDF generation)

---

## How the WAT framework works

Most AI agents fail at multi-step tasks because accuracy compounds downward — 5 steps at 90% accuracy each gives you 59% success. This system avoids that by separating concerns:

- **Workflows** define the objective, steps, and edge cases in plain language
- **The Agent** (Claude) reads the workflow and orchestrates execution
- **Tools** are Python scripts that do the actual work — API calls, file operations, data transformations

The agent reasons. The tools execute. That separation is what makes it reliable.
