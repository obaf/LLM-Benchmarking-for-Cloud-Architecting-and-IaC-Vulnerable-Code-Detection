# LLM-Benchmarking-for-Cloud-Architecting-and-IaC-Vulnerable-Code-Detection
# Terraform LLM Vulnerability Benchmark

A robust, automated benchmarking suite designed to evaluate the capability of Large Language Models (LLMs) in detecting and remediating security misconfigurations within Infrastructure as Code (Terraform).

This project uses the vulnerable [TerraGoat](https://github.com/bridgecrewio/terragoat) repository as the testbed, establishes absolute ground truth using **Checkov**, and programmatically evaluates LLMs using **Promptfoo**.

## Key Features

*   **Multi-Tiered Difficulty Levels**: 
    *   **Easy**: Exploratory vulnerability discovery.
    *   **Medium**: Proportional validation—requires models to find at least one exact ground-truth vulnerability and provide valid HCL.
    *   **Hard**: Strict format enforcement—models must catch *every* exact Checkov ID present in the file without hallucinating.
*   **Checkov Ground Truth Extraction**: A custom Python pipeline runs Checkov locally against TerraGoat to map specific `CKV_*` IDs directly to their corresponding `.tf` files.
*   **Custom Python Assertion Pipeline**: Integrates directly into Promptfoo to strictly parse JSON, validate exact ID subsets, and verify the structural syntax of LLM-generated fixes using `python-hcl2`.
*   **Provider Split Analysis**: Dynamically categorizes evaluation runs by cloud provider (AWS, Azure, GCP, Oracle/AliCloud) to measure and isolate LLM bias.
*   **Automated Analytics**: Parses Promptfoo evaluation databases to output precise breakdown tables and visually comparative bar charts via `matplotlib`.

## Prerequisites

*   **Node.js & npm** (To run `promptfoo` via `npx`)
*   **Python 3.9+** 
*   An **OpenRouter API Key** (to orchestrate LLMs universally)

### Python Dependencies
Ensure you have the following packages installed:
```bash
pip install checkov python-hcl2 matplotlib
```

## Setup & Execution

### 1. Structure the Project
If not already cloned, fetch the vulnerable Terraform repo inside the root directory:
```bash
git clone https://github.com/bridgecrewio/terragoat.git terragoat
```

### 2. Generate Ground Truth Test Data
Run the custom extractor. It will run Checkov, strip relative paths, and build the baseline `.csv` prompt templates for testing.
```bash
# Generate baseline hard dataset
python generate_tests_hard.py

# To test the medium configuration, automatically split the CSV into provider subsets:
python split_medium_tests.py
```

### 3. Run the LLM Evaluations
Export your OpenRouter API key so Promptfoo can authenticate:
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

**To run the Hard Mode evaluation:**
```bash
npx --yes promptfoo@latest eval -c promptfoo_hard.yaml --output results_hard.json
```

**To run the Medium Mode evaluation:**
Because Medium mode iterates through cloud providers separately, use the provided wrapper script:
```bash
python run_evals_medium.py
```

### 4. Analyze Results
Once the JSON result databases are generated, execute the analysis script to parse LLM grading and output PNG visualization files.
```bash
# For hard mode charts:
python analyze_results.py

# If you specifically want to run the medium mode analyzer:
python analyze_results.py
```
*(Note: Ensure you configure the Python script to target the proper JSON file prefix depending on which run you want drawn).*

## Project Architecture

*   `generate_tests_hard.py` - Runs Checkov to generate baseline JSON, parses exact `CKV` mappings, and outputs `tests_hard.csv`.
*   `validate_output.py` - Python assertion plugin for Promptfoo. Intercepts LLM JSON, parses HCL strings dynamically to prevent hallucinated code blocks, tests expected subset identifiers.
*   `promptfoo_hard.yaml` / `promptfoo_medium.yaml` - Framework configurations detailing system prompt strictness and concurrency.
*   `run_evals_medium.py` - Wrapper script traversing AWS, Azure, GCP, and Oracle tests individually.
*   `analyze_results.py` - Parses successful and failed promptfoo grades to calculate model retention rates and standardizes graph generations.

## Benchmark Subjects
This configuration natively benchmarks the following models via OpenRouter out of the box:
*   `google/gemini-3-flash-preview`
*   `deepseek/deepseek-chat-v3.1`
*   `openai/gpt-5.4-mini`

