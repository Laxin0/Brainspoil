import subprocess
from sys import argv
tests = (
    "test1.bs",
    "test2.bs"
)

if len(argv) == 2 and argv[1] == 'r':
    for f in tests:
        subprocess.run(f"python src/log.py src/tests/{f} > src/tests/{f}.record")
else:
    for f in tests:
        subprocess.run(f"python src/log.py src/tests/{f} > src/tests/{f}.out")
        subprocess.run(f"fc src/tests/{f}.out src/tests/{f}.record")

