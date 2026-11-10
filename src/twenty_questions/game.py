"""Deterministic, transcript-producing 20 Questions game engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import string
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
            guess_only = question_number > self.max_questions - 2
            prompt = self._question_prompt(
                history, question_number, self.max_questions, guess_only
            )
            raw_response = questioner.complete(prompt).strip()
            question, guess = self._parse_questioner_response(raw_response, guess_only)
            if guess is not None and guess.casefold() == secret_word.casefold():
                turns.append(
                    Turn(question_number, question, "correct guess", guess, raw_response)
                )
                won = True
                break

            answer_prompt = self._answer_prompt(secret_word, question)
            raw_answer = answerer.complete(answer_prompt).strip()
            answer = self._parse_answer(raw_answer)
            if answer is None:
                raise ValueError(
                    f"Answerer response must be yes or no, got: {raw_answer!r}"
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
    def _question_prompt(
        history: list[str], number: int, max_questions: int, guess_only: bool
    ) -> str:
        prior_turns = "\n".join(history) or "(none)"
        if guess_only:
            return (
                "You are the questioner in 20 Questions. This is a final guess "
                f"(turn {number}/{max_questions}). Based on the previous turns, "
                "return only the single answer you think is the secret word. Do "
                "not ask a question and do not include an explanation. Use the "
                "format 'GUESS: <answer>'.\nPrevious turns:\n" + prior_turns
            )
        return (
            "You are the questioner in 20 Questions. Ask one answerable yes/no "
            f"question (question {number}/{max_questions}). Previous turns:\n"
            f"{prior_turns}\n"
            "Return either 'QUESTION: <yes/no question>' or "
            "'GUESS: <single answer>'."
        )

    @staticmethod
    def _answer_prompt(secret_word: str, question: str) -> str:
        return (
            f"The secret word is {secret_word!r}. Answer this question with only "
            f"'yes' or 'no': {question}\n"
            "If the question asks whether the secret word is a specific answer, "
            "reply 'yes' only when that answer exactly matches the secret word."
        )

    @staticmethod
    def _parse_answer(response: str) -> str | None:
        normalized = response.casefold().strip().strip(string.punctuation)
        return normalized if normalized in {"yes", "no"} else None

    @staticmethod
    def _parse_questioner_response(
        response: str, guess_only: bool = False
    ) -> tuple[str, str | None]:
        if not response:
            raise ValueError("Questioner returned an empty response.")
        normalized = response.casefold()
        if guess_only:
            if normalized.startswith("guess:"):
                guess = response.split(":", 1)[1].strip()
            else:
                guess = response
            if not guess:
                raise ValueError("Questioner returned an empty guess.")
            return response, guess
        if normalized.startswith("guess:"):
            guess = response.split(":", 1)[1].strip()
            if not guess:
                raise ValueError("Questioner returned an empty guess.")
            return response, guess
        if normalized.startswith("question:"):
            question = response.split(":", 1)[1].strip()
            if not question:
                raise ValueError("Questioner returned an empty question.")
            return question, None
        return response, None
