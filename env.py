"""
TestGen Environment - Reinforcement Learning style test generation environment.

Simulates a test generation task where:
- Agent receives a function to test
- Agent submits test code
- Environment returns a mutation score (0-1) as reward
- Next function is loaded for next episode
"""

from pathlib import Path
from typing import Optional

import json
import logging
import random

from grader import evaluate_tests
from models import Action, Observation, Reward, StepResult

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
FIXTURES_PATH = BASE_DIR / "fixtures" / "functions.json"


class TestGenEnv:
    """
    Test Generation Environment.
    
    A single-step environment where:
    1. reset() loads a random function
    2. step(test_code) evaluates and scores the tests
    3. Returns reward (mutation kill rate) and next function
    
    Usage:
        env = TestGenEnv()
        obs = env.reset()  # Get first function
        
        while True:
            result = env.step(Action(test_code=my_tests))
            reward = result.reward  # 0.0 - 1.0
            obs = result.observation  # Next function
    """
    
    def __init__(self):
        """Initialize environment by loading test functions database"""
        with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.current = None
        self.current_task_level = None
        logger.info(f"TestGen environment initialized with {len(self.data)} functions")

    def _choose_task(self, task_level: Optional[str] = None):
        pool = self.data
        if task_level is not None:
            pool = [item for item in self.data if item.get("level") == task_level]
            if not pool:
                raise ValueError(f"Unknown task level: {task_level}")

        if self.current is not None and len(pool) > 1:
            filtered = [item for item in pool if item.get("code") != self.current.get("code")]
            if filtered:
                pool = filtered

        return random.choice(pool)
    
    def reset(self, task_level: Optional[str] = None):
        """
        Reset environment and load a new random function.
        
        Returns:
            Observation: A function with docstring and difficulty level
        """
        self.current_task_level = task_level
        self.current = self._choose_task(task_level)
        logger.info(f"Environment reset - loaded {self.current['level']} difficulty function: {self.current['doc']}")
        
        return Observation(
            function_code=self.current["code"],
            docstring=self.current["doc"],
            task_level=self.current["level"]
        )
    
    def step(self, action: Action):
        """
        Take a step: evaluate submitted tests and return score.
        
        Process:
        1. Validate tests against original code
        2. Run mutation testing
        3. Return score and load next function
        
        Args:
            action: Action containing test_code
            
        Returns:
            StepResult: Score, error info, and next observation
        """
        if self.current is None:
            self.reset()

        logger.info("Evaluating submitted tests...")
        score, error, killed_mutations, total_mutations = evaluate_tests(action.test_code, self.current)
        
        if error:
            logger.warning(f"Test evaluation error: {error}")
        else:
            logger.info(f"Test score: {score:.2f}")
        
        # Keep the current task active after evaluation.
        # Users can explicitly request a new task via reset/load action.
        next_obs = Observation(
            function_code=self.current["code"],
            docstring=self.current["doc"],
            task_level=self.current["level"]
        )
        
        return StepResult(
            observation=next_obs,
            reward=score,
            reward_details=Reward(
                score=score,
                killed_mutations=killed_mutations,
                total_mutations=total_mutations,
                passed_original=error is None,
            ),
            done=True,
            info=error
        )
    
    def state(self):
        """
        Get current environment state (current function).
        
        Returns:
            dict: Current function object or None if not initialized
        """
        return self.current

    def close(self):
        """Release any environment resources."""
        return None

