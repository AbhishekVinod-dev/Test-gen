"""
TestGen FastAPI Backend

Routes:
- POST /reset - Reset environment, load new function
- POST /step - Submit tests, get mutation score
- POST /generate-tests - AI-generated tests
- GET /state - Get current state
- GET / - Serve landing page
- GET /docs - Interactive API documentation (Swagger UI)
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from env import TestGenEnv
from models import Action
import os
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="🧪 TestGen API",
    description="AI-Powered Mutation Testing Challenge",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = TestGenEnv()


class TestGenerationRequest(BaseModel):
    """Request to generate tests using AI"""
    function_code: str
    docstring: str


class TestGenerationResponse(BaseModel):
    """Response with AI-generated tests"""
    test_code: str


def generate_rule_based_tests(function_code: str) -> str:
    """Generate deterministic, assertion-heavy tests as a reliable fallback."""
    match = re.search(r"def\s+(\w+)\s*\(", function_code)
    func_name = match.group(1) if match else "func"

    known_tests = {
        "add": """
def test_add_basic_cases():
    assert add(2, 3) == 5
    assert add(0, 0) == 0
    assert add(-1, -1) == -2

def test_add_mixed_signs():
    assert add(-2, 3) == 1
    assert add(10, -5) == 5
""",
        "is_even": """
def test_is_even_basic_cases():
    assert is_even(0) is True
    assert is_even(2) is True
    assert is_even(3) is False

def test_is_even_negative_cases():
    assert is_even(-2) is True
    assert is_even(-3) is False
""",
        "max_in_list": """
def test_max_in_list_common_cases():
    assert max_in_list([1, 2, 3]) == 3
    assert max_in_list([-1, -5, -3]) == -1

def test_max_in_list_edge_cases():
    assert max_in_list([7]) == 7
    assert max_in_list([]) is None
""",
        "factorial": """
def test_factorial_base_and_small_values():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(3) == 6

def test_factorial_larger_value():
    assert factorial(5) == 120
""",
        "is_palindrome": """
def test_is_palindrome_basic_cases():
    assert is_palindrome("madam") is True
    assert is_palindrome("hello") is False

def test_is_palindrome_case_and_spaces():
    assert is_palindrome("Never odd or even") is True
    assert is_palindrome("A man a plan a canal Panama") is True
""",
        "merge_sorted": """
def test_merge_sorted_basic_cases():
    assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
    assert merge_sorted([], [1, 2]) == [1, 2]

def test_merge_sorted_with_duplicates():
    assert merge_sorted([1, 2, 2], [2, 3]) == [1, 2, 2, 2, 3]
""",
        "longest_substring": """
def test_longest_substring_basic_cases():
    assert longest_substring("abcabcbb") == 3
    assert longest_substring("bbbbb") == 1

def test_longest_substring_edge_cases():
    assert longest_substring("") == 0
    assert longest_substring("pwwkew") == 3
""",
        "binary_search": """
def test_binary_search_found_cases():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 1) == 0
    assert binary_search(arr, 7) == 3
    assert binary_search(arr, 9) == 4

def test_binary_search_not_found_case():
    arr = [1, 3, 5, 7, 9]
    assert binary_search(arr, 4) == -1
""",
        "fibonacci": """
def test_fibonacci_base_and_small_values():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2

def test_fibonacci_larger_values():
    assert fibonacci(7) == 13
    assert fibonacci(10) == 55
""",
        "is_prime": """
def test_is_prime_true_cases():
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(97) is True

def test_is_prime_false_cases():
    assert is_prime(0) is False
    assert is_prime(1) is False
    assert is_prime(9) is False
    assert is_prime(100) is False
""",
    }

    if func_name in known_tests:
        return known_tests[func_name].strip()

    return f"""
def test_{func_name}_smoke():
    # Generic fallback when function is unknown.
    # Replace with tailored tests for best mutation score.
    assert callable({func_name})
""".strip()


@app.get("/")
def root():
    """Serve the landing page"""
    return FileResponse(BASE_DIR / "landing.html", media_type="text/html")


@app.get("/landing.html")
def landing_page():
    """Serve the landing page explicitly"""
    return FileResponse(BASE_DIR / "landing.html", media_type="text/html")


@app.get("/game.html")
def game_page():
    """Serve the game page"""
    return FileResponse(BASE_DIR / "game.html", media_type="text/html")


@app.post("/reset")
def reset():
    """
    Reset the environment and load a new function to test.
    
    Returns:
        Observation: Function code, docstring, and difficulty level
    """
    logger.info("API call: /reset")
    observation = env.reset()
    return observation


@app.post("/step")
def step(action: Action):
    """
    Submit test code and get mutation testing score.
    
    Args:
        action: Action object with test_code field
        
    Returns:
        StepResult: Score (reward), next observation, error info
    """
    logger.info(f"API call: /step with {len(action.test_code)} chars of test code")
    result = env.step(action)
    logger.info(f"Result: reward={result.reward:.2f}, error={result.info}")
    return result


@app.post("/generate-tests")
def generate_tests(request: TestGenerationRequest):
    """
    Generate test cases using AI (Claude/OpenAI).
    
    Args:
        request: TestGenerationRequest with function_code and docstring
        
    Returns:
        TestGenerationResponse with generated test_code
    """
    logger.info(f"API call: /generate-tests for function: {request.docstring}")
    
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
        api_base_url = os.getenv("API_BASE_URL")

        if not api_key:
            logger.warning("No API credentials configured; using rule-based test generation")
            return TestGenerationResponse(test_code=generate_rule_based_tests(request.function_code))

        if api_base_url:
            client = OpenAI(base_url=api_base_url, api_key=api_key)
        else:
            client = OpenAI(api_key=api_key)
        
        prompt = f"""Generate comprehensive pytest test cases for this function:

```python
{request.function_code}
```

Description: {request.docstring}

Requirements:
1. Write pytest format test functions
2. Test normal cases, edge cases, boundary conditions
3. Test type variations if applicable
4. Make tests that would catch common mutations (operator changes, operand removal, logic inversions)
5. Include multiple assertions per test
6. Make tests comprehensive to maximize mutation kill rate

Return ONLY the test code, no explanations or markdown.
Start directly with 'def test_'"""

        model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You write high-quality pytest tests."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.2,
        )

        test_code = (response.choices[0].message.content or "").strip()
        
        # Clean up if wrapped in markdown
        if test_code.startswith("```"):
            test_code = test_code.split("```")[1]
            if test_code.startswith("python"):
                test_code = test_code[6:]
        
        if not test_code:
            logger.warning("Empty LLM response; using rule-based test generation")
            return TestGenerationResponse(test_code=generate_rule_based_tests(request.function_code))

        logger.info(f"Generated {len(test_code)} chars of test code")
        return TestGenerationResponse(test_code=test_code.strip())
        
    except Exception as e:
        logger.error(f"Error generating tests: {e}", exc_info=True)

        logger.info("Falling back to rule-based test generation")
        return TestGenerationResponse(test_code=generate_rule_based_tests(request.function_code))


@app.get("/state")
def state():
    """
    Get the current environment state (current function).
    
    Returns:
        dict: Current function object
    """
    logger.info("API call: /state")
    return env.state()
