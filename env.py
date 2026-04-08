"""
TestGen Environment - Reinforcement Learning style test generation environment.

Simulates a test generation task where:
- Agent receives a function to test
- Agent submits test code
- Environment returns a mutation score (0-1) as reward
- Next function is loaded for next episode
"""

from pydantic import BaseModel
from typing import Optional
from grader import evaluate_tests
import json
import random
import logging

logger = logging.getLogger(__name__)


class Observation(BaseModel):
    """Observation: A function to write tests for"""
    function_code: str
    docstring: str
    task_level: str


class Action(BaseModel):
    """Action: Test code submitted by agent"""
    test_code: str


class StepResult(BaseModel):
    """Result of taking a step in the environment"""
    observation: Observation  # Next function to test
    reward: float            # Score (0-1): mutations killed / total mutations
    done: bool               # Episode done (always True for single-step)
    info: Optional[str] = None  # Error message if any


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
        with open("fixtures/functions.json") as f:
            self.data = json.load(f)
        self.current = None
        logger.info(f"TestGen environment initialized with {len(self.data)} functions")
    
    def reset(self):
        """
        Reset environment and load a new random function.
        
        Returns:
            Observation: A function with docstring and difficulty level
        """
        self.current = random.choice(self.data)
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
        logger.info("Evaluating submitted tests...")
        score, error = evaluate_tests(action.test_code, self.current)
        
        if error:
            logger.warning(f"Test evaluation error: {error}")
        else:
            logger.info(f"Test score: {score:.2f}")
        
        # Load next function for next episode
        next_obs = self.reset()
        
        return StepResult(
            observation=next_obs,
            reward=score,
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

