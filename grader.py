"""
Test grading engine for TestGen.

Evaluates test quality using mutation testing:
1. Run tests against original code (must pass)
2. Generate code mutations
3. Run tests against each mutation
4. Score = (mutations killed / total mutations)
"""

import subprocess
import tempfile
import os
import logging
import sys
from mutations import generate_mutations

logger = logging.getLogger(__name__)

# Scores must be strictly within (0, 1) for task validation.
EPSILON_SCORE = 0.01


def _clamp_open_interval(value: float, *, eps: float = EPSILON_SCORE) -> float:
    return min(max(float(value), eps), 1.0 - eps)


def run_pytest(test_code, func_code):
    """
    Execute pytest for given test and function code.
    
    Args:
        test_code: Test source code
        func_code: Function source code to test
        
    Returns:
        bool: True if all tests pass, False otherwise
    """
    with tempfile.TemporaryDirectory() as tmp:
        func_file = os.path.join(tmp, "func.py")
        test_file = os.path.join(tmp, "test_func.py")

        with open(func_file, "w") as f:
            f.write(func_code)

        with open(test_file, "w") as f:
            f.write(f"from func import *\n{test_code}")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Test execution timed out (>5 seconds)"
        except Exception as e:
            return False, "", str(e)


def evaluate_tests(test_code, func_obj):
    """
    Evaluate test quality using mutation testing.
    
    Process:
    1. Validate tests pass on original code
    2. Generate mutations
    3. Count how many mutations tests catch
    4. Return kill percentage as score
    
    Args:
        test_code: Test source code to evaluate
        func_obj: Dict with 'code' (function), 'doc' (docstring), 'level' (difficulty)
        
    Returns:
        tuple: (score, error_message)
            - score: float 0.0-1.0 (mutations killed / total mutations)
            - error_message: str or None (error description if test failed)
    """
    try:
        # Step 1: Validate test passes on original code
        passed, stdout, stderr = run_pytest(test_code, func_obj["code"])
        
        if not passed:
            error_msg = f"Tests fail on correct implementation:\n{stderr}"
            logger.warning(f"Test validation failed: {error_msg}")
            return _clamp_open_interval(0.0), error_msg, 0, 0
        
        # Step 2: Generate mutations
        mutations = generate_mutations(func_obj["code"])
        
        if not mutations:
            logger.warning("No mutations generated for code")
            return _clamp_open_interval(0.0), "Could not generate mutations", 0, 0
        
        # Step 3: Run tests against mutations
        killed = 0
        for mutation in mutations:
            passed, _, _ = run_pytest(test_code, mutation)
            if not passed:  # Test failed = mutation killed!
                killed += 1
        
        # Step 4: Calculate score
        score = _clamp_open_interval(killed / len(mutations))
        logger.info(f"Test evaluation complete: {killed}/{len(mutations)} mutations killed (score={score:.2f})")

        return score, None, killed, len(mutations)
        
    except Exception as e:
        error_msg = f"Grader error: {str(e)}"
        logger.error(error_msg)
        return _clamp_open_interval(0.0), error_msg, 0, 0

