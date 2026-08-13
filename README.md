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

## Summary of Findings

The findings below summarise the accompanying paper — *"Evaluating the Efficiency of LLMs in Cloud Architecture Design and Infra Code Fixes — A Comparative Study"* — which was produced using this benchmarking suite. Three frontier-class models were evaluated through a single OpenRouter endpoint (Google **Gemini 3 Flash Preview**, OpenAI **GPT-5.4-mini**, and **DeepSeek Chat v3.1**) across two complementary workloads: **(1)** Terraform/IaC vulnerability detection & repair, graded against **Checkov** ground truth over three escalating difficulty tiers; and **(2)** cloud-architecture reasoning, over a 30-question architectural-design set and a focused 15-question **AWS Advanced Networking (ANS-C01)** subset.

### 1. Reliability is easy; robustness is not
Under loose (*Easy*) grading, every model scores a perfect **100%** and is practically indistinguishable. As soon as structured engineering guardrails are applied, performance falls away — and under strict exact-match (*Hard*) enumeration it collapses into single digits. The right axis for comparing today's models is therefore **robustness under tightened evaluation**, not the headline pass rate.

| Model | Easy | Medium | Hard |
|---|---|---|---|
| Gemini 3 Flash Preview | 100.0% | 79.4% (27/34) | 8.8% |
| GPT-5.4-mini | 100.0% | 47.0% (16/34) | 8.8% |
| DeepSeek V3.1 | 100.0% | 58.8% (20/34) | 5.9% |

### 2. Detection coverage is low and provider-dependent
At the Medium tier (proportional credit for catching multiple vulnerabilities per file), Gemini leads across **every** cloud provider, but absolute coverage is modest and degrades sharply for less-common providers — GPT-5.4-mini and DeepSeek both score **0%** on Oracle/AliCloud files.

| Provider (files) | Gemini 3 Flash | GPT-5.4-mini | DeepSeek V3.1 |
|---|---|---|---|
| AWS (13) | 45.9% | 16.2% | 23.4% |
| Azure (12) | 42.1% | 12.0% | 9.8% |
| GCP (5) | 35.4% | 11.3% | 15.5% |
| Oracle (4) | 14.6% | 0.0% | 0.0% |

### 3. A stable ranking emerges in architectural reasoning: Gemini > DeepSeek > GPT
The same ordering recurs on both the general design set and the networking subset. On networking the dominance is **strict** — every question GPT-5.4-mini answered correctly was also answered correctly by Gemini, which solved six *additional* multi-hop items — indicating the gap is driven by **reasoning depth rather than knowledge coverage**. Note the accuracy/latency trade-off: GPT-5.4-mini is fastest but least accurate, while DeepSeek is the slowest.

**Architectural design (30 questions):**

| Model | Correct | Accuracy | Total Latency |
|---|---|---|---|
| Gemini 3 Flash Preview | 23/30 | 76.6% | 36.07 s |
| DeepSeek Chat v3.1 | 20/30 | 66.6% | 62.33 s |
| GPT-5.4-mini | 19/30 | 63.3% | 23.96 s |

**AWS Advanced Networking / ANS-C01 (15 questions):**

| Model | Correct | Accuracy |
|---|---|---|
| Gemini 3 Flash Preview | 11/15 | 73.3% |
| DeepSeek Chat v3.1 | 8/15 | 53.3% |
| GPT-5.4-mini | 5/15 | 33.3% |

### Dominant failure modes
*   **Syntactic hallucinations** — models (GPT-5.4-mini and DeepSeek especially) break strict JSON/HCL structure, e.g. escaping multi-line HCL inside a JSON value, causing assertion termination.
*   **Incomplete enumeration** — models catch the *primary* flaw (e.g. an exposed S3 bucket) but miss secondary/tertiary misconfigurations in the same file (missing KMS keys, disabled logging) that Checkov reliably flags. This is the main driver of the Hard-tier collapse.
*   **Multi-hop network reasoning** — scenarios requiring reachability reasoning across several hops (BGP advertisement, Direct Connect failover, SiteLink topologies) defeat every model.

### Practical implications
*   Loose, LLM-as-judge evaluations systematically **over-estimate** production reliability — pair them with deterministic oracles (Checkov, tfsec, OPA) before granting any model write access to infrastructure.
*   Structured-output failures dominate the failure budget at Medium/Hard tiers — wrap model output in schema-aware post-processors (JSON-mode, Pydantic, constrained decoding) rather than relying on prompt-level instructions alone.
*   Multi-hop network design (BGP, Direct Connect failover, SiteLink) remains a measurable weak point and should stay a **human-in-the-loop** decision.

## Suggestions for Further Research

1.  **Scale and stratify the benchmarks.** Grow the AWS networking set from 15 to several hundred items, stratified by ANS-C01 domain (design, implementation, management/operations, security, hybrid connectivity), and add parallel **Azure (AZ-700)** and **GCP (Professional Cloud Network Engineer)** benchmarks so cross-cloud reasoning gaps can be quantified rather than inferred.
2.  **Move from single-shot to agentic (tool-using) harnesses.** Give models MCP-based access to live cloud state, Checkov rules and the Well-Architected Framework, then measure how much of the Hard-tier collapse is recovered by tool use.
3.  **Isolate reasoning errors from format errors.** Re-run the Hard-tier IaC experiment with **constrained decoding** (Outlines, Guidance, JSON-mode) to separate genuine reasoning failures from JSON/HCL compliance failures.
4.  **Grade reasoning, not just answers.** Upgrade the Promptfoo grader from last-letter extraction to a **structured-rationale judge** that scores the chain-of-thought, so reasoning *quality* is measured directly rather than only final-answer correctness.
5.  **Test the generality of the ranking.** Cross-validate the `Gemini > DeepSeek > GPT` ordering against newer open-weight reasoning models (e.g. **Qwen-3**, **Llama-4**) to see whether it holds beyond closed-weight frontier models.

> **Caveats when extending this work:** results are a *snapshot* — OpenRouter-hosted weights are unpinned and can change silently; sample sizes are small (34 IaC files at the Medium tier, 15 networking questions), so per-model confidence intervals are wide; and certification-style questions may overlap with model training data. Full methodology, tables and discussion are in the accompanying paper.

