"""Command-line entry point for the first local prototype."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .game import BatchResult, TwentyQuestionsGame
from .models import OllamaModel
from .words import STARTER_WORDS


def _aggregate_metrics(results: list) -> dict[str, float | int | None]:
    won_games = sum(result.won for result in results)
    numeric_metrics = {
        key: [
            result.metrics[key]
            for result in results
            if isinstance(result.metrics.get(key), (int, float))
        ]
        for key in results[0].metrics
    }
    aggregate: dict[str, float | int | None] = {
        "win_rate": won_games / len(results),
        "games_won": won_games,
        "average_questions_used": sum(
            result.questions_used for result in results
        )
        / len(results),
    }
    for key, values in numeric_metrics.items():
        if key in {"questions_used", "answer_yes_count", "answer_no_count"}:
            aggregate[key] = sum(values)
        elif values:
            aggregate[f"average_{key}"] = sum(values) / len(values)
        else:
            aggregate[f"average_{key}"] = None
    return aggregate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local 20 Questions games.")
    parser.add_argument("--model", default="llama3.2", help="Ollama model name.")
    parser.add_argument(
        "--games",
        type=int,
        help="Number of games to play. If omitted, prompt in the terminal.",
    )
    parser.add_argument(
        "--secret-word",
        help="Use this word for every game instead of random starter words.",
    )
    parser.add_argument("--output", type=Path, default=Path("results/games.json"))
    args = parser.parse_args()

    games = args.games
    if games is None:
        try:
            games = int(input("How many games should be played? ").strip())
        except ValueError as error:
            parser.error("game count must be a positive integer")
            raise AssertionError from error
    if games < 1:
        parser.error("game count must be a positive integer")

    model = OllamaModel(model=args.model, name=args.model)
    results = []
    for game_number in range(1, games + 1):
        secret_word = args.secret_word or random.choice(STARTER_WORDS)["word"]
        result = TwentyQuestionsGame().play(secret_word, model, model)
        results.append(result)
        outcome = "won" if result.won else "lost"
        print(
            f"Completed game {game_number}/{games}: {outcome} "
            f"({result.questions_used} questions)"
        )
    batch = BatchResult(
        games_requested=games,
        games=tuple(results),
        aggregate_metrics=_aggregate_metrics(results),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(batch.to_dict(), indent=2), encoding="utf-8")
    print(f"Saved {games} games to {args.output}")


if __name__ == "__main__":
    main()
