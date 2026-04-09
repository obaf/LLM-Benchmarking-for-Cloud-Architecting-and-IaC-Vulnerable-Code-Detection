import os
import csv

providers = ['aws', 'azure', 'gcp', 'oracle']
base_dir = "terragoat/terraform"

for provider in providers:
    tests_file = f"tests_{provider}.csv"
    provider_dir = os.path.join(base_dir, provider)
    
    with open(tests_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["terraform_code", "assert_rubric"])
        
        if os.path.exists(provider_dir):
            for root, dirs, files in os.walk(provider_dir):
                for file in files:
                    if file.endswith('.tf'):
                        filepath = os.path.join(root, file).replace('\\', '/')
                        writer.writerow([f"file://{filepath}", "Must identify the primary security misconfigurations"])

    print(f"Generated {tests_file}")
