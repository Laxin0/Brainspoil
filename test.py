#!/usr/bin/python3

import subprocess
from sys import argv
from glob import glob

PYTHON = "python"
COMP = "fc"
TEST_FOLDER = "tests"

test_files = ''

def record():
    global test_files
    for file in test_files:
        with open(f"{file}.expect", "w") as out_file:
            subprocess.run([PYTHON, "src/log.py", f"{file}"], stdout = out_file)
    print(f"All {len(test_files)} tests recorded.")

failed = []
def run():
    global test_files
    for file in test_files:
        with open(f"{file}.out", "w") as out_file:
            subprocess.run([PYTHON, "src/log.py", f"{file}"], stdout = out_file)
        if subprocess.run([COMP, f"{file}.out", f"{file}.expect"]).returncode != 0:
            failed.append(file)
    if len(failed) == 0:
        print(f"All {len(test_files)} test are OK!")
    else:
        print(f"{len(failed)} of {len(test_files)} tests are Failed:")
        print("\n".join(failed))


if __name__ == "__main__":
    if len(argv) < 2 or (argv[1] != "rec" and argv[1] != "run"):
        print("Usage: python test.py rec | run")
        print("rec for record tests' output, run for compare output with expected)")
        exit(0)
    
    test_files = glob(TEST_FOLDER+"/*.bs")
    if argv[1] == "rec":
        record()
    else:
        run()
