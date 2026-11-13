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
    questioner = FakeModel(["QUESTION: Is it alive?", "GUESS: penguin"])
    answerer = FakeModel(["Yes."])

    result = TwentyQuestionsGame(max_questions=20).play(
        "penguin", questioner, answerer
    )

    assert result.won is True
    assert result.questions_used == 2
    assert result.turns[0].answer == "yes"
    assert result.turns[1].guess == "penguin"


def test_game_accepts_explicit_guess_without_asking_answerer():
    questioner = FakeModel(["GUESS: piano"])
    answerer = FakeModel([])

    result = TwentyQuestionsGame(max_questions=1).play(
        "piano", questioner, answerer
    )

    assert result.won is True
    assert result.turns[0].answer == "correct guess"


def test_final_two_turns_are_guess_only():
    questioner = FakeModel(["penguin", "GUESS: penguin"])
    answerer = FakeModel([])

    result = TwentyQuestionsGame(max_questions=2).play(
        "penguin", questioner, answerer
    )

    assert result.won is True
    assert result.questions_used == 1


def test_game_normalizes_answer_punctuation():
    questioner = FakeModel(["QUESTION: Is it round?"])
    answerer = FakeModel([" no! "])

    result = TwentyQuestionsGame(max_questions=1).play(
        "piano", questioner, answerer
    )

    assert result.turns[0].answer == "no"


def test_game_rejects_non_binary_answer():
    questioner = FakeModel(["QUESTION: Is it round?"])
    answerer = FakeModel(["maybe"])

    with pytest.raises(ValueError, match="yes or no"):
        TwentyQuestionsGame(max_questions=1).play("piano", questioner, answerer)


def test_game_stops_at_question_limit():
    questioner = FakeModel(["QUESTION: Is it blue?", "QUESTION: Is it large?"])
    answerer = FakeModel(["no"])

    result = TwentyQuestionsGame(max_questions=1).play(
        "piano", questioner, answerer
    )

    assert result.won is False
    assert result.questions_used == 1


def test_game_records_research_metrics():
    questioner = FakeModel(
        [
            "QUESTION: Is it an animal?",
            "QUESTION: Is it an animal?",
            "GUESS: piano",
            "GUESS: piano",
        ]
    )
    answerer = FakeModel(["yes", "yes", "no", "no"])

    result = TwentyQuestionsGame(max_questions=4).play(
        "penguin", questioner, answerer
    )

    assert result.metrics["answer_variation_entropy"] > 0.0
    assert result.metrics["question_quality_score"] > 0.0
    assert result.metrics["answer_truthfulness_score"] == 1.0
    assert result.metrics["total_latency_seconds"] >= 0.0
