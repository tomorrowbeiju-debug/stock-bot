# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r'c:\Users\Administrator\WorkBuddy\Claw\stock_bot')

# Add remote
result = subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/tomorrowbeiju-debug/stock-bot.git'], capture_output=True, text=True, shell=True)
print("Remote:", result.returncode, result.stderr)

# Push
result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], capture_output=True, text=True, shell=True)
print("Push:", result.returncode)
print(result.stdout)
print(result.stderr)
