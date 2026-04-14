"""
AI Web Research Agent - Core Engine
Vaixus Technologies | Built by VIJAYARAJAN S
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Production-grade AI research agent.
    Supports both Groq (default) and Gemini.
    """

    def __init__(self, model_provider: str = "groq"):
        self.provider = model_provider.lower()

        if self.provider == "gemini":
            from google import genai
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file.")
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Initialized with Gemini provider")

        elif self.provider == "groq":
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in .env file.")
            self.groq_client = Groq(api_key=api_key)
            logger.info("Initialized with Groq provider")

        else:
            raise ValueError("model_provider must be 'groq' or 'gemini'")

        # Serper setup
        self.serper_key = os.getenv("SERPER_API_KEY")

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def search_web(self, query: str, num_results: int = 8) -> list[dict]:
        """Search the web using Serper API or fallback to DuckDuckGo."""
        logger.info(f"Searching: {query}")

        if self.serper_key:
            return self._serper_search(query, num_results)
        else:
            return self._duckduckgo_search(query, num_results)

    def _serper_search(self, query: str, num_results: int = 8) -> list[dict]:
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query, "num": num_results})
        headers = {"X-API-KEY": self.serper_key, "Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            return results
        except Exception as e:
            logger.warning(f"Serper failed: {e}. Falling back to DuckDuckGo.")
            return self._duckduckgo_search(query, num_results)

    def _duckduckgo_search(self, query: str, num_results: int = 8) -> list[dict]:
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=num_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo failed: {e}")
            return []

    def scrape_page(self, url: str, max_chars: int = 3000) -> str:
        try:
            response = requests.get(url, headers=self.headers, timeout=8)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "form"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            return " ".join(text.split())[:max_chars]
        except Exception as e:
            logger.warning(f"Could not scrape {url}: {e}")
            return ""

    def gather_intelligence(self, topic: str) -> dict:
        logger.info(f"Gathering intelligence on: {topic}")

        general_results = self.search_web(f"{topic} company overview business")
        news_results = self.search_web(f"{topic} latest news 2025 2026")
        competitor_results = self.search_web(f"{topic} competitors market position")

        all_results = {
            "general": general_results[:4],
            "news": news_results[:3],
            "competitors": competitor_results[:3]
        }

        scraped_content = []
        for result in general_results[:4]:
            url = result.get("url", "")
            if url:
                content = self.scrape_page(url)
                if content:
                    scraped_content.append({
                        "source": url,
                        "title": result.get("title", ""),
                        "content": content
                    })
                    logger.info(f"Scraped: {url}")

        return {
            "search_results": all_results,
            "scraped_content": scraped_content
        }

    def generate_report(self, topic: str, raw_data: dict) -> str:
        logger.info(f"Generating report using {self.provider.upper()}...")

        # Build context
        search_context = ""
        for category, results in raw_data["search_results"].items():
            search_context += f"\n\n[{category.upper()} RESULTS]\n"
            for r in results:
                search_context += f"- {r['title']}: {r['snippet']}\n"

        scraped_context = ""
        for page in raw_data["scraped_content"][:3]:
            scraped_context += f"\n\n[FROM: {page['title']}]\n{page['content'][:1500]}\n"

        prompt = f"""
You are a professional business intelligence analyst.
Analyze the following research data about "{topic}" and generate a comprehensive structured report.

SEARCH DATA:
{search_context}

SCRAPED CONTENT:
{scraped_context}

Generate the report with these exact sections:

## EXECUTIVE SUMMARY
[2-3 sentences]

## COMPANY / TOPIC OVERVIEW
[Clear description]

## KEY FINDINGS
[5-7 bullet points]

## RECENT DEVELOPMENTS
[Latest news and announcements]

## MARKET POSITION
[Competitors and industry standing]

## OPPORTUNITIES & RISKS
[Opportunities and risks]

## INTELLIGENCE RATING
[HIGH / MEDIUM / LOW] with short reason.

Be factual and concise. Do not hallucinate.
"""

        try:
            if self.provider == "groq":
                completion = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1800,
                )
                return completion.choices[0].message.content

            elif self.provider == "gemini":
                from google.genai import types
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                return response.text

        except Exception as e:
            logger.error(f"Report generation failed with {self.provider}: {e}")
            return f"Report generation failed: {str(e)}"

    def save_report(self, topic: str, report: str, raw_data: dict) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:30]

        os.makedirs("output", exist_ok=True)

        md_filename = f"output/{safe_topic}_{timestamp}.md"
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(f"# Research Report: {topic}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Agent:** Vaixus AI Research Agent v1.0 ({self.provider.upper()})\n\n")
            f.write("---\n\n")
            f.write(report)
            f.write("\n\n---\n")
            f.write(f"*Report generated by Vaixus Technologies*\n")

        json_filename = f"output/{safe_topic}_{timestamp}_raw.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump({
                "topic": topic,
                "timestamp": timestamp,
                "sources_found": len(raw_data["scraped_content"]),
                "search_results_count": sum(len(v) for v in raw_data["search_results"].values()),
                "raw_data": raw_data
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Report saved: {md_filename}")
        return md_filename

    def run(self, topic: str) -> dict:
        logger.info(f"=== VAIXUS RESEARCH AGENT STARTED ===")
        logger.info(f"Topic: {topic}")

        try:
            raw_data = self.gather_intelligence(topic)

            if not raw_data["search_results"]["general"]:
                return {
                    "success": False,
                    "error": "No search results found. Check API keys.",
                    "report": None,
                    "file": None
                }

            report = self.generate_report(topic, raw_data)
            file_path = self.save_report(topic, report, raw_data)

            logger.info("=== RESEARCH COMPLETE ===")

            return {
                "success": True,
                "topic": topic,
                "report": report,
                "file": file_path,
                "sources_used": len(raw_data["scraped_content"]),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Agent failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "report": None,
                "file": None
            }