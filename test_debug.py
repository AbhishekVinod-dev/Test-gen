import subprocess
import tempfile
import os
import sys
import time

# Create temp files
with tempfile.TemporaryDirectory() as tmp:
    func_file = os.path.join(tmp, 'func.py')
    test_file = os.path.join(tmp, 'test_func.py')
    
    with open(func_file, 'w') as f:
        f.write('def add(a, b):\n    return a + b')
    
    with open(test_file, 'w') as f:
        f.write('''from func import *

def test_add():
    assert add(2, 3) == 5
''')
    
    print('Test file at:', test_file)
    print('Running pytest...')
    cmd = [sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short']
    print('Command:', ' '.join(cmd))
    
    start = time.time()
    try:
        # Try with text=False first
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=20,
            text=False,
            cwd=tmp
        )
        elapsed = time.time() - start
        print(f'Completed in {elapsed:.2f}s')
        print(f'Return code: {result.returncode}')
        print(f'STDOUT:\n{result.stdout.decode()}')
        print(f'STDERR:\n{result.stderr.decode()}')
    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - start
        print(f'Timeout after {elapsed:.2f}s')
        print(f'Output so far: {e.stdout}')
