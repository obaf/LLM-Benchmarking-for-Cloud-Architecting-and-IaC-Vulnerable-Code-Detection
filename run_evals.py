import subprocess
import os

providers = ['aws', 'azure', 'gcp', 'oracle']

openrouter_key = os.environ.get("OPENROUTER_API_KEY", "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")
os.environ["OPENROUTER_API_KEY"] = openrouter_key

for provider in providers:
    yaml_content = f"""description: "Terraform Vulnerability Detection Benchmark - {provider.upper()}"
prompts:
  - "You are a cloud security expert. Review the following Terraform code and list any security vulnerabilities you find. Be concise. \\n\\n{{{{terraform_code}}}}"
providers:
  - openrouter:openai/gpt-5.4-mini
  - openrouter:google/gemini-3-flash-preview
  - openrouter:deepseek/deepseek-chat-v3.1
tests: tests_{provider}.csv
"""
    yaml_file = f"promptfoo_{provider}.yaml"
    with open(yaml_file, "w") as f:
        f.write(yaml_content)
    
    print(f"Running eval for {provider}...")
    subprocess.run(["npx.cmd", "--yes", "promptfoo@latest", "eval", "-c", yaml_file, "--output", f"results_{provider}.json"])
    print(f"Finished {provider}")
