import subprocess
import os

providers = ["aws", "azure", "gcp", "oracle"]
env = os.environ.copy()
env['OPENROUTER_API_KEY'] = "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"

for p in providers:
    print(f"\n--- Running evaluation for {p.upper()} ---")
    test_csv = f"tests_medium_{p}.csv"
    output_json = f"results_medium_{p}.json"
    
    cmd = f"cmd.exe /c npx --yes promptfoo@latest eval -c promptfoo_medium.yaml -t {test_csv} -o {output_json} -j 3"
    
    result = subprocess.run(cmd, env=env, shell=True)
    if result.returncode != 0:
        print(f"Evaluation for {p} encountered an error.")
    else:
        print(f"Finished evaluation for {p}.")
