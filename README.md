# CSE519-Final-Project
Project Proposal 
CSE-519

20 Questions with LLMs

Test it on various LLMs
See how they perform
Investigate how to improve them
Build Akinator with the best LLM
https://huggingface.co/lmarena-ai
https://www.kaggle.com/competitions/llm-20-questions/overview 


Datasets we have
What we plan to do with datasets
Basic Statistics on dataset
Roadblocks
Preliminary results

How Good Are LLMs at 20 Questions?    (MS and/or PhD Students)

In the game of 20 questions, one player selects a secret word or thing, which a second player must identify by asking a series of true/false questions.   The winner (guesser or questioner) is determined by failure or success after twenty questions.    LLMs are in principle capable of suggesting random-ish words, and asking/answering questions.    How good are they at 20 questions?   Getting two models to play 20 questions with each other will not be difficult: the interesting thing is to carefully evaluate what they are doing and how well they are doing it.

A successful project here will convincingly evaluate different pairs of models against each other.   Perhaps this is done through an agent-type architecture, but I will want to see results of all possible pairs of at least four different LLM models, each playing the role of guesser and questioner against each other.
Evaluation is a critical thing here.   You need to design and perform experiments which convincingly compare models in different roles, answering questions like:
Do models perform better when the same model is used in both roles in different sessions, or is one model better than others in a particular role?
How well do models do selecting words/concepts uniformly at random?   Compare them to a truly random generator for nouns, places, people, and general vocabulary worlds.
How good are the questions the models ask?  In theory each question should try to half the space of remaining possibilities.
How good are they at accurately answering questions about the hidden word?  The guesser can mislead the questioner by giving misleading answers, which is bad/cheating.
There is previous work here.   Do a literature search on papers which have tried to evaluate models at 20 questions.   I will expect to see a research summary in your progress report.

# Abstract (Introduction/ General Plan)


The game of 20 questions involves a subject (person) having an object, profession or concept in their mind while players question the subject to narrow down and guess the object, having the limit of 20 questions to do so. Our project aims to evaluate the performance of Large Language Models (LLMs) for both the subject and the player. 

Throughout the years, LLMs have gotten better at emulating human conversations and at playing games at levels comparable (or even exceeding) professions. We aim to see how well they have really gotten and which LLMs in particular perform best as such tasks. We will also look into reasons why certain LLMs are better than others, investigating how they were trained (using which data) and for which original purpose they were built.  


# Background (Previous Work Done in this Domain)

According to C. R. S. Kumar in his paper Large Language Models(LLM) for Automating 20 Questions Game, the game used to be accomplished by “using decision trees, heuristic algorithms, or rule-based systems that map out potential objects and the corresponding questions that might lead to their identification. However, these methods often struggle with the complexity and variability inherent in human language, especially when dealing with ambiguous or less common objects.” He goes on to utilize 1 LLM as a guesser, and another LLM as the answerer. This paper then uses the data gathered from a Kaggle competition, along with other sources.
In 2024, Kaggle hosted a competition to see who could create the best LLM for the 20 Questions game. Each team had the ability to submit bots who would play games with other bots, and the winner of the competition utilized a dual LLM approach to handle different types of questions, with a Meta Llama 3 8B Instruct as the general purpose LLM, and a DeepSeek Math model to handle complex mathematical oriented questions about the keyword. The competition featured a 2 vs 2 cooperative game, with each team consisting of a questioner and answerer. Our work will be simplifying this to a one versus one conventional implementation.
While previous work has demonstrated that LLMs can participate in 20 Questions, there is still an opportunity to investigate how different language models compare when assigned different roles.
An important consideration is that the questioner and answerer require different capabilities. The questioner must demonstrate strategic reasoning, effective question selection, and the ability to interpret previous responses. The answerer must demonstrate factual knowledge, consistency, and the ability to interpret questions accurately. Because of this, a model that performs well as a questioner may not perform well as an answerer. Since our project requires each model to perform both roles, the models chosen need to be well balanced for both of these, and the winning model may not be the best guesser, or the best answerer.

# Approach (Plan in Detail)

Finding LLMs and researching what they were created for. Playing 20 questions directly with each LLM (as a player/questioner) and evaluating performance based on how many questions it takes for them to guess our object, and if they guessed correctly or not. 

We will develop a scoring algorithm to score each LLM on its performance. 

We will also investigate which topics each LLM performs best on.

Pairwise comparison: We will put pairs of LLMs head to head (even with themselves) and see how well they do against each other and what concepts they come up with. Are the concepts repetitive?, which LLM does best when it comes to coming up with concepts more randomly?

For the questions asked we will evaluate and score them based on how the question was at narrowing the search down.

For each pair we will initially have a hypothesis as to how it will perform based on how it was trained. Then we will see if our hypothesis holds true, and what could explain their actual behaviour. 

List of Models and brief description of their purpose: [TBD]

From

# Data / Datasets
Data on LLM performance for how well they do for selecting words/concepts uniformly at random?   Compare them to a truly random generator for nouns, places, people, and general vocabulary worlds.


# Evaluation Plan

Our evaluation will focus on four dimensions: overall game performance, word selection, question quality, and answer accuracy. Game performance will be measured by win rate and the average number of questions needed to identify the hidden word. We will test all pairings of at least four LLMs, with each model serving as both questioner and answerer, to identify differences between roles and self-play. Word selection will be evaluated by comparing the distribution and diversity of model-selected words across categories (nouns, places, people, and general vocabulary) against a uniform random baseline. Question quality will be measured by how effectively questions reduce the remaining candidate space, using information gain to assess how closely questions divide possibilities in half. Answer accuracy will be evaluated by comparing responses against known facts about the hidden word, measuring truthfulness and consistency while identifying misleading or contradictory answers.
If time and resources permit, we will also evaluate computational efficiency using metrics such as peak RAM and VRAM usage, response time, and token consumption. This will allow us to examine the tradeoff between game performance and resource requirements, identifying models that achieve comparable results with fewer computational resources.




# Next Steps

# References

Kumar, C. R. S. (n.d.). *Large language models (LLM) for automating 20 questions game*.

Mongan, Z., Sernau, L., Lifferth, W., Doerschuk-Tiberi, B., Holbrook, R., Cukierski, W., & Howard, A. (2024). *LLM 20 questions*. Kaggle. https://www.kaggle.com/competitions/llm-20-questions/overview

Zhang, Y., Lu, J., & Jaitly, N. (2024). Probing the multi-turn planning capabilities of LLMs via 20 question games. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*.