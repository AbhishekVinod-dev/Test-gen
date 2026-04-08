"""Data models for testgen_env OpenEnv package."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Observation(BaseModel):
    function_code: str
    docstring: str
    task_level: str


class Action(BaseModel):
    test_code: str


class Reward(BaseModel):
    score: float
    killed_mutations: int
    total_mutations: int
    passed_original: bool = True


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Optional[str] = None
    reward_details: Reward | None = None
