# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'c:\Users\Administrator\WorkBuddy\Claw\stock_bot')

# Add all files
result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True, shell=True)
print("Add:", result.returncode)

# Commit
result = subprocess.run(['git', 'commit', '-m', 'first commit'], capture_output=True, text=True, shell=True)
print("Commit:", result.returncode)
print(result.stdout)
print(result.stderr)
