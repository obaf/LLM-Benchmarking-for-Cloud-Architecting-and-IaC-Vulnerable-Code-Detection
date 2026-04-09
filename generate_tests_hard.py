import subprocess
import json
import csv
import os
import sys

def run_checkov():
    print("Running checkov...")
    checkov_path = r"C:\Users\Admin\AppData\Roaming\Python\Python314\Scripts\checkov.cmd"
    if not os.path.exists(checkov_path):
        print(f"Checkov not found at {checkov_path}")
        checkov_path = "checkov"

    result = subprocess.run(
        [checkov_path, "-d", "terragoat/terraform", "--output", "json"],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_checkov_output(stdout_str):
    try:
        parsed = json.loads(stdout_str)
    except json.JSONDecodeError:
        print("Failed to decode Checkov output. Attempting to parse the last valid JSON block:")
        # sometimes checkov prints warnings at the beginning
        start_idx = stdout_str.find("[")
        if start_idx == -1:
            start_idx = stdout_str.find("{")
        if start_idx != -1:
            try:
                parsed = json.loads(stdout_str[start_idx:])
            except Exception as e:
                print(e)
                return {}
        else:
            return {}
    
    if isinstance(parsed, dict):
        parsed = [parsed]
        
    file_checks = {}
    
    for report in parsed:
        if report.get("check_type") == "terraform" or "terraform" in report.get("check_type", ""):
            results = report.get("results", {})
            failed_checks = results.get("failed_checks", [])
            for check in failed_checks:
                file_path = check.get("file_path", "")
                check_id = check.get("check_id")
                
                file_path = file_path.lstrip("/\\")
                
                full_path = os.path.join("terragoat/terraform", file_path).replace("\\", "/")

                if not os.path.exists(full_path): continue
                
                if full_path not in file_checks:
                    file_checks[full_path] = set()
                file_checks[full_path].add(check_id)
                
    return file_checks

def main():
    stdout_str = run_checkov()
    file_checks = parse_checkov_output(stdout_str)
    
    if not file_checks:
        print("No terraform vulnerabilities found by checkov or parsing failed.")
        return
        
    csv_file = "tests_hard.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["terraform_code", "expected_ids"])
        
        for file_path, checks in file_checks.items():
            expected_ids = ",".join(sorted(list(checks)))
            writer.writerow([f"file://{file_path}", expected_ids])
            
    print(f"Generated {csv_file} with {len(file_checks)} files.")

if __name__ == "__main__":
    main()
