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
import pytest
import threading
from mutations import generate_mutations

logger = logging.getLogger(__name__)

# Scores must be strictly within (0, 1) for task validation.
EPSILON_SCORE = 0.01


def _clamp_open_interval(value: float, *, eps: float = EPSILON_SCORE) -> float:
    return min(max(float(value), eps), 1.0 - eps)


def run_pytest(test_code, func_code):
    """
    Execute test code directly without subprocess.
    
    Args:
        test_code: Test source code
        func_code: Function source code to test
        
    Returns:
        tuple: (bool, stdout, stderr) - True if tests pass, False otherwise
    """
    import traceback
    import io
    import sys
    from contextlib import redirect_stdout, redirect_stderr
    
    # Combine code
    combined_code = f"{func_code}\n{test_code}"
    
    # Create a namespace for execution
    namespace = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        # Execute the combined code
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(combined_code, namespace)
        
        # Now run test functions
        failures = []
        for name, obj in namespace.items():
            if name.startswith('test_') and callable(obj):
                try:
                    obj()
                except AssertionError as e:
                    failures.append(str(e) or f"Test {name} failed")
                except Exception as e:
                    failures.append(f"Test {name} errored: {e}")
        
        if failures:
            return False, "", "\n".join(failures)
        
        # If no test functions found, that's an error
        test_funcs = [name for name in namespace.keys() if name.startswith('test_')]
        if not test_funcs:
            return False, "", "No test functions found (must start with 'test_')"
        
        return True, stdout_capture.getvalue(), stderr_capture.getvalue()
        
    except SyntaxError as e:
        return False, "", f"Syntax error in test code: {e}"
    except Exception as e:
        return False, "", f"Error executing tests: {e}\n{traceback.format_exc()}"





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

