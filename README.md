# CSE519 20 Questions with LLMs

This project evaluates local language models playing the roles of questioner
and answerer in a game of 20 Questions. The research proposal is available in
[PROJECT_PROPOSAL.md](PROJECT_PROPOSAL.md).

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/) for running a local model

## Setup

From the repository root, create a virtual environment and install the project:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[test]"
```

## Run the tests

```bash
.venv/bin/python -m pytest
```

## Run games

Start Ollama and download a model:

```bash
ollama pull llama3.2
```

Run a requested number of games. If `--games` is omitted, the command prompts
for the count in the terminal:

```bash
.venv/bin/python -m twenty_questions.cli \
  --model llama3.2 \
  --games 10
```

Each game randomly selects a word from the starter vocabulary. To use one
deterministic word for every game, add `--secret-word penguin`. All transcripts
and aggregate metrics are saved to `results/games.json` by default; use
`--output` to choose another path.

The JSON includes these auditable metrics for each game and averages/counts
across the batch:

- guess performance: win indicator and questions used
- question quality: information gain for recognized vocabulary categories
- answer variation: normalized entropy of yes/no answers
- answerer truthfulness: correctness against curated vocabulary facts
- question humanness: deterministic clarity, format, length, and repetition heuristics
- computational efficiency: per-turn/total latency and available process RAM delta

Unavailable hardware measurements, such as VRAM when the host does not expose
it, are recorded as `null` rather than estimated.

The game strips common `<think>...</think>` reasoning blocks before parsing
model answers. If an answer is still not clearly `yes` or `no`, it automatically
re-prompts the answerer with a strict one-word format before failing explicitly.

## Project layout

```text
src/twenty_questions/  Game engine, model adapter, vocabulary, and CLI
tests/                  Unit tests
results/                Generated game transcripts
PROJECT_PROPOSAL.md     Research proposal and references
```
