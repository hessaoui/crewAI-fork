#!/usr/bin/env python
from pathlib import Path

from dotenv import load_dotenv

# Load .env sitting at the project root (../../.env from this file).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from marketing_crew.crew import MarketingCrew, load_brand_inputs


def run():
    """Run the research -> ad-angle crew for the configured brand."""
    Path("outputs").mkdir(exist_ok=True)
    inputs = load_brand_inputs()
    result = MarketingCrew().crew().kickoff(inputs=inputs)
    print("\n===== RESULT =====\n")
    print(result)


if __name__ == "__main__":
    run()
