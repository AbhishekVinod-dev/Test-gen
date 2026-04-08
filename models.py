"""Data models for testgen_env OpenEnv package."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Observation:
    function_code: str
    docstring: str
    task_level: str
