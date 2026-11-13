import json

import pytest

from twenty_questions import cli


class FakeModel:
    name = "fake"

    def complete(self, prompt: str) -> str:
        if "Answer this question with only" in prompt:
            return "yes"
        if "final guess" in prompt:
            return "GUESS: penguin"
        return "QUESTION: Is it an animal?"


def test_cli_runs_requested_number_of_games_with_random_words(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "OllamaModel", lambda model, name: FakeModel())
    output = tmp_path / "games.json"

    monkeypatch.setattr(
        "sys.argv",
        ["twenty_questions.cli", "--games", "3", "--output", str(output)],
    )
    cli.main()

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["games_requested"] == 3
    assert payload["games_played"] == 3
    assert len(payload["games"]) == 3
    assert 0.0 <= payload["aggregate_metrics"]["win_rate"] <= 1.0


def test_cli_prompts_when_game_count_is_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "OllamaModel", lambda model, name: FakeModel())
    monkeypatch.setattr("builtins.input", lambda prompt: "1")
    output = tmp_path / "games.json"
    monkeypatch.setattr(
        "sys.argv",
        ["twenty_questions.cli", "--secret-word", "penguin", "--output", str(output)],
    )

    cli.main()

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["games_requested"] == 1
    assert payload["games"][0]["secret_word"] == "penguin"


@pytest.mark.parametrize("games", ["0", "-1"])
def test_cli_rejects_non_positive_game_count(monkeypatch, games):
    monkeypatch.setattr("sys.argv", ["twenty_questions.cli", "--games", games])

    with pytest.raises(SystemExit):
        cli.main()
