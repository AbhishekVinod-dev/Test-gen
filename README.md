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

TestGen is a mutation-testing benchmark for evaluating how well tests kill buggy variants of a function.

The web UI includes:
- [landing.html](landing.html)
- [game.html](game.html)

## What it does

The app loads a function from [fixtures/functions.json](fixtures/functions.json), lets you write pytest-style tests, and scores them by how many mutations they catch.

It is built to measure test quality, not just code coverage.

## Core flow

1. Click **Load New Task** to get a function.
2. Write tests in the editor.
3. Submit the tests.
4. Receive a score from 0% to 100% based on mutation kills.

## API Endpoints

- `POST /reset`
- `POST /step`
- `POST /generate-tests`
- `GET /state`

## Local Setup

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

## Demo Script

Run the baseline inference script to see the structured output used by the benchmark:

```bash
python inference.py
```

## Files

- [app.py](app.py)
- [env.py](env.py)
- [grader.py](grader.py)
- [mutations.py](mutations.py)
- [inference.py](inference.py)
- [fixtures/functions.json](fixtures/functions.json)

## Notes

The project is intentionally small and self-contained so it can be used as a coding benchmark or demo.
