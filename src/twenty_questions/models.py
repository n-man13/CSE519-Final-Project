"""Model interfaces and a local Ollama adapter."""

from __future__ import annotations

import json
import shutil
import sys
import subprocess
from dataclasses import dataclass
from typing import Protocol
from urllib import request


def process_memory_bytes() -> int | None:
    """Return this process's resident memory when the host exposes it."""
    if sys.platform == "win32":
        import ctypes

        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("page_fault_count", ctypes.c_ulong),
                ("peak_working_set_size", ctypes.c_size_t),
                ("working_set_size", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if ctypes.windll.psapi.GetProcessMemoryInfo(
            ctypes.windll.kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            return int(counters.working_set_size)
        return None
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(usage * (1024 if sys.platform == "darwin" else 1))
    except (ImportError, AttributeError):
        return None


def gpu_memory_bytes() -> int | None:
    """Return total memory used by visible GPUs when nvidia-smi is available."""
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return None
    try:
        completed = subprocess.run(
            [
                executable,
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            check=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    values = []
    for line in completed.stdout.splitlines():
        try:
            values.append(int(line.strip()) * 1024 * 1024)
        except ValueError:
            continue
    return sum(values) if values else None


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
