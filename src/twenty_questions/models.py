"""Model interfaces and a local Ollama adapter."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol
from urllib import request


class ModelAdapter(Protocol):
    """Interface required by the game engine."""

    name: str

    def complete(self, prompt: str) -> str:
        """Return a model response for a prompt."""


@dataclass
class OllamaModel:
    """Small standard-library adapter for a model served by Ollama."""

    model: str
    endpoint: str = "http://localhost:11434/api/generate"
    name: str = "ollama"

    def complete(self, prompt: str) -> str:
        payload = json.dumps(
            {"model": self.model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        http_request = request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except Exception as error:
            raise RuntimeError(
                f"Could not query Ollama at {self.endpoint}: {error}"
            ) from error

        result = body.get("response")
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("Ollama returned no usable text response.")
        return result.strip()
