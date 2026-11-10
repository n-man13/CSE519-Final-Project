"""Deterministic, transcript-producing 20 Questions game engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .models import ModelAdapter


@dataclass(frozen=True)
class Turn:
    question_number: int
    question: str
    answer: str
    guess: str | None
    raw_response: str


@dataclass(frozen=True)
class GameResult:
    secret_word: str
    questioner_model: str
    answerer_model: str
    won: bool
    questions_used: int
    turns: tuple[Turn, ...]

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["turns"] = [asdict(turn) for turn in self.turns]
        return result


class TwentyQuestionsGame:
    def __init__(self, max_questions: int = 20) -> None:
        if max_questions < 1:
            raise ValueError("max_questions must be positive.")
        self.max_questions = max_questions

    def play(
        self,
        secret_word: str,
        questioner: ModelAdapter,
        answerer: ModelAdapter,
    ) -> GameResult:
        if not secret_word.strip():
            raise ValueError("secret_word must not be empty.")

        turns: list[Turn] = []
        history: list[str] = []
        won = False

        for question_number in range(1, self.max_questions + 1):
            prompt = self._question_prompt(secret_word, history, question_number)
            raw_response = questioner.complete(prompt).strip()
            question, guess = self._parse_questioner_response(raw_response)
            if guess is not None and guess.casefold() == secret_word.casefold():
                turns.append(
                    Turn(question_number, question, "correct guess", guess, raw_response)
                )
                won = True
                break

            answer_prompt = self._answer_prompt(secret_word, question)
            answer = answerer.complete(answer_prompt).strip()
            if answer.casefold() not in {"yes", "no"}:
                raise ValueError(
                    f"Answerer response must be yes or no, got: {answer!r}"
                )
            turns.append(Turn(question_number, question, answer, guess, raw_response))
            history.append(f"Q: {question}\nA: {answer}")

        return GameResult(
            secret_word=secret_word,
            questioner_model=questioner.name,
            answerer_model=answerer.name,
            won=won,
            questions_used=len(turns),
            turns=tuple(turns),
        )

    @staticmethod
    def _question_prompt(secret_word: str, history: list[str], number: int) -> str:
        del secret_word  # The prompt intentionally does not reveal the answer.
        prior_turns = "\n".join(history) or "(none)"
        return (
            "You are the questioner in 20 Questions. Ask one answerable yes/no "
            f"question (question {number}/20). Previous turns:\n{prior_turns}\n"
            "Return only the question."
        )

    @staticmethod
    def _answer_prompt(secret_word: str, question: str) -> str:
        return (
            f"The secret word is {secret_word!r}. Answer this question with only "
            f"'yes' or 'no': {question}"
        )

    @staticmethod
    def _parse_questioner_response(response: str) -> tuple[str, str | None]:
        if not response:
            raise ValueError("Questioner returned an empty response.")
        if response.lower().startswith("guess:"):
            guess = response.split(":", 1)[1].strip()
            if not guess:
                raise ValueError("Questioner returned an empty guess.")
            return response, guess
        return response, None
