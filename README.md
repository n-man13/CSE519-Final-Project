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

## Run one game

Start Ollama and download a model:

```bash
ollama pull llama3.2
```

Run the game:

```bash
.venv/bin/python -m twenty_questions.cli \
  --model llama3.2 \
  --secret-word penguin
```

The structured transcript is saved to `results/game.json` by default.

## Project layout

```text
src/twenty_questions/  Game engine, model adapter, vocabulary, and CLI
tests/                  Unit tests
results/                Generated game transcripts
PROJECT_PROPOSAL.md     Research proposal and references
```
