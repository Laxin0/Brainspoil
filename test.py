import subprocess
from sys import argv

test_files = [
    "math.bs",
    "err_eof.bs"
]

def record():
    for file in test_files:
        subprocess.run(["python", "src\\log.py", f"tests\\{file}", ">", f"tests\\{file}.expect"], shell=True)

failed = []
def run():
    for file in test_files:
        subprocess.run(["python", "src\\log.py", f"tests\\{file}", ">", f"tests\\{file}.out"], shell=True)
        if subprocess.run(["fc", "/a", f"tests\\{file}.out", f"tests\\{file}.expect"], shell=True).returncode != 0:
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