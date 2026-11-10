"""Command-line entry point for the first local prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .game import TwentyQuestionsGame
from .models import OllamaModel


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one local 20 Questions game.")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name.")
    parser.add_argument("--secret-word", default="penguin")
    parser.add_argument("--output", type=Path, default=Path("results/game.json"))
    args = parser.parse_args()

    model = OllamaModel(model=args.model, name=args.model)
    result = TwentyQuestionsGame().play(args.secret_word, model, model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")
    print(f"Saved {result.questions_used} turns to {args.output}")


if __name__ == "__main__":
    main()
