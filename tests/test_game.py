from dataclasses import dataclass

import pytest

from twenty_questions.game import TwentyQuestionsGame


@dataclass
class FakeModel:
    responses: list[str]
    name: str = "fake"

    def complete(self, prompt: str) -> str:
        del prompt
        if not self.responses:
            raise AssertionError("Fake model ran out of responses.")
        return self.responses.pop(0)


def test_game_records_turns_and_accepts_correct_guess():
    questioner = FakeModel(["Is it alive?", "Guess: penguin"])
    answerer = FakeModel(["yes"])

    result = TwentyQuestionsGame(max_questions=20).play(
        "penguin", questioner, answerer
    )

    assert result.won is True
    assert result.questions_used == 2
    assert result.turns[0].answer == "yes"
    assert result.turns[1].guess == "penguin"


def test_game_rejects_non_binary_answer():
    questioner = FakeModel(["Is it round?"])
    answerer = FakeModel(["maybe"])

    with pytest.raises(ValueError, match="yes or no"):
        TwentyQuestionsGame(max_questions=1).play("piano", questioner, answerer)


def test_game_stops_at_question_limit():
    questioner = FakeModel(["Is it blue?", "Is it large?"])
    answerer = FakeModel(["no"])

    result = TwentyQuestionsGame(max_questions=1).play(
        "piano", questioner, answerer
    )

    assert result.won is False
    assert result.questions_used == 1
