import subprocess
import os

os.chdir(r'c:\Users\Administrator\WorkBuddy\Claw\stock_bot')

# Git add
subprocess.run(['git', 'add', '.'], shell=True)

# Git commit
subprocess.run(['git', 'commit', '-m', 'first commit'], shell=True)

print("Done!")
