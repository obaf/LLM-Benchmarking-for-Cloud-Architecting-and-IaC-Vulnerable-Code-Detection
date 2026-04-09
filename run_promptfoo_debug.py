import subprocess
import os

env = os.environ.copy()
env['OPENROUTER_API_KEY'] = "input secret key here"

result = subprocess.run('cmd.exe /c npx --yes promptfoo@latest eval -c promptfoo_hard.yaml', shell=True, capture_output=True, text=True, env=env)
with open('debug_output.txt', 'w', encoding='utf-8') as f:
    f.write(result.stdout)
    f.write("\n================\nstderr:\n")
    f.write(result.stderr)
