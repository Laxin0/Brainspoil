import subprocess
from sys import argv

PYTHON = "python3"
COMP = "diff"

test_files = [
    "math.bs",
    "err_eof.bs"
]

def record():
    for file in test_files:
        with open(f"tests/{file}.expect", "w") as out_file:
            subprocess.run([PYTHON, "src/log.py", f"tests/{file}"], stdout = out_file)

failed = []
def run():
    for file in test_files:
        with open(f"tests/{file}.out", "w") as out_file:
            subprocess.run([PYTHON, "src/log.py", f"tests/{file}"], stdout = out_file)
        if subprocess.run([COMP, f"tests/{file}.out", f"tests/{file}.expect"]).returncode != 0:
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

    if argv[1] == "rec":
        record()
    else:
        run()
