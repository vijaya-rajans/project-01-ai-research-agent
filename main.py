"""
AI Web Research Agent - Main Entry Point
Vaixus Technologies | Built by Soorya S.V.

Usage:
    python main.py                          # Interactive mode
    python main.py --topic "Tesla"          # Direct mode
    python main.py --topic "OpenAI" --quiet # Quiet mode (no console output)
"""

import argparse
import sys
from agent.research_agent import ResearchAgent


def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║         VAIXUS AI RESEARCH AGENT v1.0                ║
║         Built by Soorya S.V. | vaixus.tech           ║
╚══════════════════════════════════════════════════════╝
    """)


def main():
    parser = argparse.ArgumentParser(
        description="AI Web Research Agent - Generate intelligence reports on any topic"
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Company name or topic to research",
        default=None
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress report output to console"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["groq", "gemini"],
        default="groq",
        help="AI provider to use (default: groq)"
    )

    args = parser.parse_args()

    print_banner()

    # Get topic
    if args.topic:
        topic = args.topic.strip()
    else:
        print("Enter the company or topic to research.")
        print("Examples: 'Tesla', 'OpenAI', 'Zomato India', 'AI in healthcare'\n")
        topic = input("Research topic: ").strip()

    if not topic:
        print("Error: Topic cannot be empty.")
        sys.exit(1)

    print(f"\nStarting research on: '{topic}'")
    print("This may take 30-60 seconds...\n")

    # Run agent
    agent = ResearchAgent(model_provider=args.provider)
    result = agent.run(topic)
    
    if result["success"]:
        print("\n" + "="*60)
        print("RESEARCH COMPLETE")
        print("="*60)

        if not args.quiet:
            print(result["report"])

        print("\n" + "="*60)
        print(f"Report saved to: {result['file']}")
        print(f"Sources used: {result['sources_used']}")
        print(f"Completed at: {result['timestamp']}")
        print("="*60 + "\n")

    else:
        print(f"\nResearch failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
