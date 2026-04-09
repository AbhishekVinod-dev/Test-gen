"""Baseline inference runner for TestGen."""

from __future__ import annotations

import os
import textwrap
from typing import Optional

from openai import OpenAI

from app import generate_rule_based_tests
from env import Action, TestGenEnv

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
TASK_NAME = os.getenv("MY_ENV_V4_TASK", "testgen")
BENCHMARK = os.getenv("MY_ENV_V4_BENCHMARK", "testgen_env")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")
TEMPERATURE = 0.0
MAX_TOKENS = 900
SUCCESS_SCORE_THRESHOLD = 0.10
TASK_LEVELS = ("easy", "medium", "hard")
EPSILON_SCORE = 0.01


def clamp_open_interval(value: float, *, eps: float = EPSILON_SCORE) -> float:
    return min(max(float(value), eps), 1.0 - eps)


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_value = error if error else "null"
    error_value = error_value.replace("\n", " | ")
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_value}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: list[float]) -> None:
    rewards_value = ",".join(f"{value:.2f}" for value in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_value}",
        flush=True,
    )


def build_prompt(task_level: str, function_code: str, docstring: str, history: list[str]) -> str:
    history_block = "\n".join(history[-4:]) if history else "None"
    return textwrap.dedent(
        f"""
        Task level: {task_level}
        Function under test:
        ```python
        {function_code}
        ```

        Docstring: {docstring}

        Prior attempts:
        {history_block}

        Write concise pytest tests that maximize mutation kills.
        Return only test code.
        """
    ).strip()


def generate_tests(
    client: Optional[OpenAI],
    task_level: str,
    function_code: str,
    docstring: str,
    history: list[str],
) -> str:
    if client is None:
        return generate_rule_based_tests(function_code)

    prompt = build_prompt(task_level, function_code, docstring, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You write high-quality pytest tests."},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```", 2)[1]
            text = text.removeprefix("python").strip()
        return text or generate_rule_based_tests(function_code)
    except Exception:
        return generate_rule_based_tests(function_code)


def summarize_action(test_code: str) -> str:
    if not test_code.strip():
        return "empty_tests"
    first_line = test_code.strip().splitlines()[0].strip()
    if first_line.startswith("def "):
        return first_line.split("(", 1)[0].replace("def ", "")
    return "generated_tests"


def run_episode(env: TestGenEnv, client: Optional[OpenAI], task_level: str) -> tuple[float, bool, list[float]]:
    history: list[str] = []
    rewards: list[float] = []
    score = 0.0
    success = False

    log_start(task=task_level, env=BENCHMARK, model=MODEL_NAME)

    observation = env.reset(task_level=task_level)
    try:
        test_code = generate_tests(
            client=client,
            task_level=task_level,
            function_code=observation.function_code,
            docstring=observation.docstring,
            history=history,
        )

        result = env.step(Action(test_code=test_code))
        reward = clamp_open_interval(result.reward or 0.0)
        rewards.append(reward)
        score = clamp_open_interval(reward)
        success = score >= SUCCESS_SCORE_THRESHOLD and result.info is None

        history.append(f"task={task_level} reward={reward:.2f}")
        log_step(step=1, action=summarize_action(test_code), reward=reward, done=result.done, error=result.info)
        log_end(success=success, steps=1, score=score, rewards=rewards)

    finally:
        env.close()

    return score, success, rewards


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN) if HF_TOKEN else None
    env = TestGenEnv()

    for task_level in TASK_LEVELS:
        run_episode(env=env, client=client, task_level=task_level)


if __name__ == "__main__":
    main()
