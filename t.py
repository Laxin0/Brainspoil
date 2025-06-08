

from sys import argv
import subprocess 

subprocess.run(['python3', 'src/main.py', argv[1], '-o', 'build/out.bf'])
subprocess.run(['python3', 'src/bfc.py', 'build/out.bf', 'build/out.s'])
subprocess.run(['fasm', 'build/out.s'])
print("exit code:", subprocess.run(['./build/out']).returncode)