from grader import evaluate_tests

# Test with a simple function
func_obj = {
    'code': 'def add(a, b):\n    return a + b',
    'doc': 'sum two numbers',
    'level': 'easy'
}

# Test code that should pass
test_code = '''
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
'''

score, error, killed, total = evaluate_tests(test_code, func_obj)
print(f'Test passed!')
print(f'Score: {score}')
print(f'Error: {error}')
print(f'Killed: {killed}/{total}')
