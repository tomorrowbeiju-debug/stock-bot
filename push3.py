# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'c:\Users\Administrator\WorkBuddy\Claw\stock_bot')

# Remove existing remote
subprocess.run(['git', 'remote', 'remove', 'origin'], capture_output=True, text=True, shell=True)

# Add remote directly
result = subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/tomorrowbeiju-debug/stock-bot.git'], capture_output=True, text=True, shell=True)
print("Remote add:", result.returncode, result.stderr)

# Push
result = subprocess.run(['git', 'push', '-u', 'origin', 'master'], capture_output=True, text=True, shell=True)
print("Push:", result.returncode)
print(result.stdout)
print(result.stderr)
