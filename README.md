# AI Web Research Agent

**Autonomous business intelligence. Any company. Any topic. Instant structured report.**

Built by [Soorya S.V.](https://linkedin.com/in/sooryasv) | [Vaixus Technologies](https://vaixus.tech)

---

## What It Does

Give it a company name or topic. It searches the web autonomously, scrapes the top sources, and delivers a structured intelligence report — in under 60 seconds.

No manual browsing. No copy-pasting. Just input and output.

```
Input:  "Tesla Motors"
Output: Executive Summary + Key Findings + Recent News + 
        Market Position + Opportunities & Risks
        Saved as .md file with full audit trail
```

---

## Demo

```bash
$ python main.py --topic "Zomato India"

=== VAIXUS RESEARCH AGENT STARTED ===
Searching: Zomato India company overview business
Searching: Zomato India latest news 2024 2025
Scraped: https://en.wikipedia.org/wiki/Zomato
Scraped: https://www.zomato.com/about
Generating AI report...

## EXECUTIVE SUMMARY
Zomato is India's leading food delivery platform...

## KEY FINDINGS
- Operates in 800+ cities across India
- Revenue grew 70% YoY in FY2024
...

Report saved to: output/Zomato_India_20250413_143022.md
Sources used: 4
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Engine | Google Gemini 1.5 Flash |
| Web Search | Serper.dev API / DuckDuckGo |
| Scraping | BeautifulSoup4 + Requests |
| API Layer | FastAPI |
| Runtime | Python 3.11+ |

---

## Setup — 4 Steps

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/project-01-ai-research-agent
cd project-01-ai-research-agent
```

**2. Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Open .env and add your GEMINI_API_KEY
```

Get your free Gemini API key at: https://aistudio.google.com/apikey

---

## Usage

### Command Line
```bash
# Interactive mode
python main.py

# Direct mode
python main.py --topic "OpenAI"

# Quiet mode (saves file, no console output)
python main.py --topic "Tesla" --quiet
```

### REST API
```bash
# Start the API server
uvicorn api:app --reload --port 8000

# API docs available at:
http://localhost:8000/docs
```

**Start a research job:**
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Tesla Motors"}'

# Response:
{
  "job_id": "abc-123",
  "status": "queued",
  "message": "Research started. Poll /research/abc-123 for results."
}
```

**Get results:**
```bash
curl http://localhost:8000/research/abc-123

# Response when complete:
{
  "job_id": "abc-123",
  "status": "completed",
  "report": "## EXECUTIVE SUMMARY\n...",
  "sources_used": 4
}
```

---

## Output Format

Every report contains:

- **Executive Summary** — 2-3 sentence overview
- **Company / Topic Overview** — Core business description
- **Key Findings** — 5-7 bullet points of important facts
- **Recent Developments** — Latest news and announcements
- **Market Position** — Competitors and industry standing
- **Opportunities & Risks** — Strategic intelligence
- **Intelligence Rating** — Confidence level with reasoning

Reports saved as `.md` files with JSON audit trail in `/output` directory.

---

## Project Structure

```
project-01-ai-research-agent/
├── agent/
│   └── research_agent.py    # Core agent logic
├── output/                  # Generated reports (gitignored)
├── main.py                  # CLI entry point
├── api.py                   # FastAPI REST interface
├── requirements.txt         # Dependencies
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

---

## API Keys

| Key | Required | Free Tier | Get It |
|-----|----------|-----------|--------|
| GEMINI_API_KEY | Yes | 1M tokens/day | [aistudio.google.com](https://aistudio.google.com/apikey) |
| SERPER_API_KEY | No | 2,500 searches/month | [serper.dev](https://serper.dev) |

Without SERPER_API_KEY, the agent uses DuckDuckGo automatically. No cost.

---

## What Clients Pay For This

This agent solves a real business problem:
- Sales teams research prospects manually — takes 30-45 minutes per company
- This agent does it in 60 seconds
- Typical project rate: ₹5,000–8,000 one-time or ₹2,000/month automated

---

## Built With

- [Google Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Serper.dev](https://serper.dev)
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search)

---

## Author

**Soorya S.V.**
Founder & AI Automation Developer, Vaixus Technologies

- Website: [vaixus.tech](https://vaixus.tech)
- LinkedIn: [linkedin.com/in/sooryasv](https://linkedin.com/in/sooryasv)
- Email: soorya@vaixus.tech

---

*Project 1 of 25 — Vaixus AI Automation Portfolio*

