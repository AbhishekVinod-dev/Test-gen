import sys
print("Starting test...")

try:
    print("Importing pytest...")
    import pytest
    print(f"Pytest imported: {pytest.__version__}")
except Exception as e:
    print(f"Failed to import pytest: {e}")
    sys.exit(1)

try:
    print("Importing grader...")
    from grader import evaluate_tests
    print("Grader imported successfully")
except Exception as e:
    print(f"Failed to import grader: {e}")
    sys.exit(1)

print("About to call evaluate_tests...")

# Test with a simple function
func_obj = {
    'code': 'def add(a, b):\n    return a + b',
    'doc': 'sum two numbers',
    'level': 'easy'
}

# Test code that should pass
test_code = 'def test_add():\n    assert add(2, 3) == 5'

print(f"Calling evaluate_tests...")
score, error, killed, total = evaluate_tests(test_code, func_obj)
print(f'Test completed!')
print(f'Score: {score}')
print(f'Error: {error}')
