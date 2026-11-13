"""Deterministic, transcript-producing 20 Questions game engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import math
import re
import string
import time
from typing import Any

from .models import ModelAdapter, gpu_memory_bytes, process_memory_bytes
from .words import STARTER_WORDS


@dataclass(frozen=True)
class Turn:
    question_number: int
    question: str
    answer: str
    guess: str | None
    raw_response: str
    response_latency_seconds: float = 0.0
    answer_latency_seconds: float | None = None


@dataclass(frozen=True)
class GameResult:
    secret_word: str
    questioner_model: str
    answerer_model: str
    won: bool
    questions_used: int
    turns: tuple[Turn, ...]
    metrics: dict[str, float | int | None] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["turns"] = [asdict(turn) for turn in self.turns]
        return result


@dataclass(frozen=True)
class BatchResult:
    games_requested: int
    games: tuple[GameResult, ...]
    aggregate_metrics: dict[str, float | int | None]

    def to_dict(self) -> dict[str, Any]:
        return {
            "games_requested": self.games_requested,
            "games_played": len(self.games),
            "games": [game.to_dict() for game in self.games],
            "aggregate_metrics": self.aggregate_metrics,
        }


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
        memory_before = process_memory_bytes()
        vram_before = gpu_memory_bytes()

        for question_number in range(1, self.max_questions + 1):
            guess_only = question_number > self.max_questions - 2
            prompt = self._question_prompt(
                history, question_number, self.max_questions, guess_only
            )
            question_started = time.perf_counter()
            raw_response = questioner.complete(prompt).strip()
            question_latency = time.perf_counter() - question_started
            question, guess = self._parse_questioner_response(raw_response, guess_only)
            if guess is not None and guess.casefold() == secret_word.casefold():
                turns.append(
                    Turn(
                        question_number,
                        question,
                        "correct guess",
                        guess,
                        raw_response,
                        question_latency,
                    )
                )
                won = True
                break

            answer_prompt = self._answer_prompt(secret_word, question)
            answer_started = time.perf_counter()
            raw_answer = answerer.complete(answer_prompt).strip()
            answer_latency = time.perf_counter() - answer_started
            answer = self._parse_answer(raw_answer)
            if answer is None:
                raise ValueError(
                    f"Answerer response must be yes or no, got: {raw_answer!r}"
                )
            turns.append(
                Turn(
                    question_number,
                    question,
                    answer,
                    guess,
                    raw_response,
                    question_latency,
                    answer_latency,
                )
            )
            history.append(f"Q: {question}\nA: {answer}")

        result = GameResult(
            secret_word=secret_word,
            questioner_model=questioner.name,
            answerer_model=answerer.name,
            won=won,
            questions_used=len(turns),
            turns=tuple(turns),
            metrics={},
        )
        memory_after = process_memory_bytes()
        vram_after = gpu_memory_bytes()
        memory_delta = (
            memory_after - memory_before
            if memory_before is not None and memory_after is not None
            else None
        )
        vram_delta = (
            vram_after - vram_before
            if vram_before is not None and vram_after is not None
            else None
        )
        return replace(
            result, metrics=self._metrics(result, memory_delta, vram_delta)
        )

    @staticmethod
    def _metrics(
        result: GameResult, memory_delta: int | None, vram_delta: int | None
    ) -> dict[str, float | int | None]:
        answers = [turn.answer for turn in result.turns if turn.answer in {"yes", "no"}]
        yes_count = answers.count("yes")
        no_count = answers.count("no")
        answer_count = len(answers)
        if answer_count:
            probabilities = [yes_count / answer_count, no_count / answer_count]
            entropy = -sum(
                probability * math.log2(probability)
                for probability in probabilities
                if probability
            )
        else:
            entropy = 0.0

        question_scores = []
        seen_questions: set[str] = set()
        quality_scores = []
        truthfulness_scores = []
        for turn in result.turns:
            normalized = re.sub(r"\s+", " ", turn.question.strip().casefold())
            score = 0.0
            if normalized.endswith("?"):
                score += 0.25
            if normalized.startswith(
                ("is ", "are ", "do ", "does ", "can ", "has ", "have ")
            ):
                score += 0.35
            if 5 <= len(normalized.split()) <= 20:
                score += 0.25
            if normalized and normalized not in seen_questions:
                score += 0.15
            seen_questions.add(normalized)
            question_scores.append(min(score, 1.0))
            category = next(
                (
                    candidate
                    for candidate in ("animal", "object", "place", "profession")
                    if candidate in normalized
                ),
                None,
            )
            if category is not None:
                category_count = sum(
                    word["category"] == category for word in STARTER_WORDS
                )
                probability = category_count / len(STARTER_WORDS)
                if probability in {0.0, 1.0}:
                    information_score = 0.0
                else:
                    entropy = -(
                        probability * math.log2(probability)
                        + (1 - probability) * math.log2(1 - probability)
                    )
                    information_score = entropy
                quality_scores.append(information_score)
                secret_category = next(
                    (
                        word["category"]
                        for word in STARTER_WORDS
                        if word["word"] == result.secret_word
                    ),
                    None,
                )
                expected = "yes" if secret_category == category else "no"
                if secret_category is not None and turn.answer in {"yes", "no"}:
                    truthfulness_scores.append(float(turn.answer == expected))

        total_latency = sum(turn.response_latency_seconds for turn in result.turns)
        total_latency += sum(
            turn.answer_latency_seconds or 0.0 for turn in result.turns
        )
        return {
            "guess_score": 1.0 if result.won else 0.0,
            "questions_used": result.questions_used,
            "answer_variation_entropy": entropy,
            "answer_yes_count": yes_count,
            "answer_no_count": no_count,
            "question_humanness_score": (
                sum(question_scores) / len(question_scores)
                if question_scores
                else 0.0
            ),
            "question_quality_score": (
                sum(quality_scores) / len(quality_scores)
                if quality_scores
                else None
            ),
            "answer_truthfulness_score": (
                sum(truthfulness_scores) / len(truthfulness_scores)
                if truthfulness_scores
                else None
            ),
            "total_latency_seconds": total_latency,
            "ram_bytes_delta": memory_delta,
            "vram_bytes_delta": vram_delta,
        }

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
                "not ask a question and do not include an explanation or "
                "reasoning tags. Use the "
                "format 'GUESS: <answer>'.\nPrevious turns:\n" + prior_turns
            )
        return (
            "You are the questioner in 20 Questions. Ask one answerable yes/no "
            f"question (question {number}/{max_questions}). Previous turns:\n"
            f"{prior_turns}\n"
            "Return either 'QUESTION: <yes/no question>' or "
            "'GUESS: <single answer>'. Do not include an explanation or "
            "reasoning tags."
        )

    @staticmethod
    def _answer_prompt(secret_word: str, question: str) -> str:
        return (
            f"The secret word is {secret_word!r}. Answer this question with only "
            f"'yes' or 'no': {question}\nDo not include an explanation, "
            "markdown, or reasoning tags.\n"
            "If the question asks whether the secret word is a specific answer, "
            "reply 'yes' only when that answer exactly matches the secret word."
        )

    @staticmethod
    def _parse_answer(response: str) -> str | None:
        normalized = TwentyQuestionsGame._remove_reasoning(response)
        normalized = normalized.casefold().strip().strip(string.punctuation)
        return normalized if normalized in {"yes", "no"} else None

    @staticmethod
    def _parse_questioner_response(
        response: str, guess_only: bool = False
    ) -> tuple[str, str | None]:
        response = TwentyQuestionsGame._remove_reasoning(response)
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

    @staticmethod
    def _remove_reasoning(response: str) -> str:
        """Remove common model reasoning blocks before parsing its final answer."""
        without_reasoning = re.sub(
            r"<think>.*?</think>", "", response, flags=re.IGNORECASE | re.DOTALL
        )
        return without_reasoning.strip()
