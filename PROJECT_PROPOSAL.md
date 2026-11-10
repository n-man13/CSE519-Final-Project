# CSE519 Final Project Proposal

## Project Overview

### 20 Questions with LLMs

- Test the performance of various LLMs.
- Investigate how to improve their performance.
- Build an Akinator-style game with the best-performing LLM.

Related resources:

- https://huggingface.co/lmarena-ai
- https://www.kaggle.com/competitions/llm-20-questions/overview

## Motivation

### How Good Are LLMs at 20 Questions?

In the game of 20 Questions, one player selects a secret word or thing, which a second player must identify by asking a series of true/false questions. The winner is determined by whether the guesser identifies the secret within twenty questions. LLMs are capable of suggesting words and asking or answering questions, but their performance in this setting requires careful evaluation.

A successful project will evaluate different pairs of models against each other. We plan to test all possible pairings of at least four LLMs, with each model playing both the questioner and answerer roles.

The evaluation will address the following questions:

- Do models perform better when the same model is used in both roles?
- Is one model better suited to a particular role?
- How well do models select words or concepts uniformly at random?
- How do model-selected words compare with a truly random generator for nouns, places, people, and general vocabulary?
- How effectively do models ask questions that divide the remaining possibilities?
- How accurately and consistently do models answer questions about the hidden word?

Previous work has evaluated models on 20 Questions, so the project will include a literature review and research summary.

## Abstract

The game of 20 Questions involves a subject having an object, profession, or concept in mind while another player asks questions to narrow down and identify it within twenty questions. This project will evaluate the performance of Large Language Models (LLMs) when acting as both the subject and the questioner.

LLMs have improved at emulating human conversations and playing games at levels comparable to or exceeding those of humans. We will investigate how well different LLMs perform at 20 Questions and why some models perform better than others. We will also examine how their training data and intended purposes may affect their performance.

## Background and Previous Work

According to C. R. S. Kumar in *Large Language Models (LLM) for Automating 20 Questions Game*, the game was previously approached using decision trees, heuristic algorithms, or rule-based systems mapping potential objects to questions. These methods can struggle with the complexity and variability of human language, especially for ambiguous or uncommon objects. Kumar uses one LLM as the guesser and another as the answerer, using data from a Kaggle competition and other sources.

In 2024, Kaggle hosted a competition to develop LLMs for 20 Questions. Teams submitted bots that played against other bots. The winning approach used a dual-LLM system with Meta Llama 3 8B Instruct as a general-purpose model and a DeepSeek Math model for complex mathematical questions about the keyword. The competition used a cooperative 2-versus-2 game, with each team consisting of a questioner and answerer. Our work will simplify this to a conventional one-versus-one implementation.

Although previous work has shown that LLMs can participate in 20 Questions, there remains an opportunity to investigate how different models compare when assigned different roles.

The questioner and answerer require different capabilities. The questioner must demonstrate strategic reasoning, effective question selection, and the ability to interpret previous responses. The answerer must demonstrate factual knowledge, consistency, and accurate question interpretation. Therefore, a model that performs well as a questioner may not perform well as an answerer. Since each model will perform both roles, the selected models should be evaluated for both capabilities.

## Approach

We will research the purpose and training background of each selected LLM. We will then have each model play 20 Questions as a questioner and evaluate performance based on the number of questions needed to guess the object and whether the guess is correct.

We will develop a scoring algorithm to evaluate each LLM. We will also investigate which topics each model handles best.

For pairwise comparisons, pairs of LLMs—including self-play pairings—will play against each other. We will analyze their performance, the concepts they select, and whether their selected concepts are repetitive or diverse.

Questions will be evaluated based on how effectively they narrow the search space. For each model pairing, we will begin with a hypothesis based on the models' training and intended use, then compare the hypothesis with the observed behavior.

The list of models and their intended purposes is still to be determined.

## Data and Datasets

We will collect data on how well LLMs select words or concepts uniformly at random. Model-selected words will be compared with a truly random generator for nouns, places, people, and general vocabulary.

## Evaluation Plan

Our evaluation will focus on four dimensions:

1. **Overall game performance:** Measure win rate and the average number of questions needed to identify the hidden word. Test all pairings of at least four LLMs, with each model serving as both questioner and answerer.
2. **Word selection:** Compare the distribution and diversity of model-selected words across categories against a uniform random baseline.
3. **Question quality:** Measure how effectively questions reduce the remaining candidate space using information gain, including how closely questions divide possibilities in half.
4. **Answer accuracy:** Compare responses against known facts about the hidden word and measure truthfulness, consistency, and misleading or contradictory answers.

If time and resources permit, we will also evaluate computational efficiency using peak RAM and VRAM usage, response time, and token consumption. This will allow us to examine the tradeoff between game performance and resource requirements.

## References

Kumar, C. R. S. (n.d.). *Large language models (LLM) for automating 20 questions game*.

Mongan, Z., Sernau, L., Lifferth, W., Doerschuk-Tiberi, B., Holbrook, R., Cukierski, W., & Howard, A. (2024). *LLM 20 questions*. Kaggle. https://www.kaggle.com/competitions/llm-20-questions/overview

Zhang, Y., Lu, J., & Jaitly, N. (2024). Probing the multi-turn planning capabilities of LLMs via 20 question games. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*.
