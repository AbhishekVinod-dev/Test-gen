"""Client helpers for the testgen_env OpenEnv package."""

from __future__ import annotations

from typing import Any, Dict


def make_action(test_code: str) -> Dict[str, Any]:
    """Build an action payload compatible with openenv.yaml action_space."""
    return {"test_code": test_code}
