# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'c:\Users\Administrator\WorkBuddy\Claw\stock_bot')

# Check current branch
result = subprocess.run(['git', 'branch'], capture_output=True, text=True, shell=True)
print("Branches:", result.stdout)

# Push current branch to main
result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], capture_output=True, text=True, shell=True)
print("Push:", result.returncode)
print(result.stdout)
print(result.stderr)
