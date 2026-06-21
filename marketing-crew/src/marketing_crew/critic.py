#!/usr/bin/env python
"""Score a set of ad hooks with the Groq-pinned critic agent.

Usage:
    python -m marketing_crew.critic [HOOKS_FILE] [LABEL]

    HOOKS_FILE  defaults to outputs/ad_angles.md
    LABEL       defaults to a label derived from the file name
                (e.g. outputs/ad_angles_groq.md -> "groq")

Writes the scores to outputs/critic_scores_<label>.md (and, transiently,
outputs/critic_scores.md as declared in critic_tasks.yaml).
"""
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from marketing_crew.crew import build_critic_crew, load_brand_inputs


def _derive_label(path: Path) -> str:
    stem = path.stem  # e.g. "ad_angles_groq" or "ad_angles"
    if stem.startswith("ad_angles_"):
        return stem[len("ad_angles_"):]
    if stem == "ad_angles":
        return "default"
    return stem


def run():
    args = sys.argv[1:]
    hooks_path = Path(args[0]) if args else Path("outputs/ad_angles.md")
    label = args[1] if len(args) > 1 else _derive_label(hooks_path)

    if not hooks_path.exists():
        sys.exit(f"Hooks file not found: {hooks_path}")

    hooks = hooks_path.read_text(encoding="utf-8")
    Path("outputs").mkdir(exist_ok=True)

    brand_context = load_brand_inputs().get("brand_context", "")
    result = build_critic_crew().kickoff(
        inputs={
            "ad_angles_path": str(hooks_path),
            "ad_hooks": hooks,
            "brand_context": brand_context,
        }
    )

    # critic_tasks.yaml writes outputs/critic_scores.md; keep a labeled copy so
    # each backend's scores are preserved for comparison.
    src = Path("outputs/critic_scores.md")
    dst = Path(f"outputs/critic_scores_{label}.md")
    if src.exists():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"\n===== CRITIC SCORES ({label}) -> {dst} =====\n")
    print(result)


if __name__ == "__main__":
    run()
