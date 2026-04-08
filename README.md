---
title: Testgen Env Environment Server
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 8000
tags:
  - openenv
---

# TestGen

TestGen is a mutation-testing benchmark for evaluating how well an agent can write tests for small Python functions. The environment simulates a real software-engineering task: test design, not a toy game.

## Motivation

The goal is to measure whether an agent can produce tests that catch subtle logic changes. A strong solution should go beyond coverage and kill real mutants generated from the source code.

## Environment Overview

The environment exposes a single-step RL-style loop:

- `reset()` loads a function to test and returns an observation.
- `step(action)` evaluates submitted tests, returns a reward, and loads the next function.
- `state()` returns the current task state.

The UI routes are:

- [landing.html](landing.html)
- [game.html](game.html)

## Action and Observation Space

Observation:

- `function_code`: the Python function source code.
- `docstring`: the plain-language task description.
- `task_level`: one of `easy`, `medium`, or `hard`.

Action:

- `test_code`: pytest-style test code to evaluate.

Reward:

- `score`: mutation kill rate in `[0.0, 1.0]`.
- `killed_mutations`: number of mutants the tests fail on.
- `total_mutations`: total generated mutants evaluated.

## Tasks

The environment provides three task tiers:

1. `easy`: simple arithmetic and parity checks such as `add` and `is_even`.
2. `medium`: list and string utilities such as `max_in_list`, `factorial`, `is_palindrome`, and `fibonacci`.
3. `hard`: algorithmic functions such as `merge_sorted`, `longest_substring`, `binary_search`, and `is_prime`.

Each task uses a deterministic grader based on mutation testing. Success is measured by how many mutants are killed while still passing on the correct implementation.

## Scoring

The score is computed as:

`score = killed_mutations / total_mutations`

The grader also rejects tests that fail on the original implementation and times out slow tests.

## Baseline Scores

Measured with the included inference runner:

- Easy: `1.00`
- Medium: `1.00`
- Hard: `1.00`

The baseline script uses the OpenAI client when `HF_TOKEN` or `OPENAI_API_KEY` is available, and falls back to the deterministic rule-based generator when offline.

## Setup

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Validate

```bash
openenv validate
```

## Baseline Inference

```bash
python inference.py
```

The script prints `[START]`, `[STEP]`, and `[END]` lines for each task level in order: easy, medium, hard.

## Files

- [app.py](app.py)
- [env.py](env.py)
- [grader.py](grader.py)
- [mutations.py](mutations.py)
- [inference.py](inference.py)
- [fixtures/functions.json](fixtures/functions.json)

## Notes

The project is containerized for Hugging Face Spaces and validated with `openenv validate`.
