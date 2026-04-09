import json
import matplotlib.pyplot as plt
import os

providers = ["aws", "azure", "gcp", "oracle"]

for provider in providers:
    results_file = f"results_medium_{provider}.json"
    if not os.path.exists(results_file):
        continue
        
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = {}
    results_list = []
    if 'results' in data:
        if isinstance(data['results'], list):
            results_list = data['results']
        elif 'results' in data['results'] and isinstance(data['results']['results'], list):
            results_list = data['results']['results']
    else:
        if isinstance(data, list):
            results_list = data

    for r in results_list:
        p = r.get("provider", {}).get("id", "Unknown")
        if p not in stats:
            stats[p] = {"pass": 0, "fail": 0, "error": 0, "score_sum": 0.0, "total": 0}
            
        stats[p]["total"] += 1
        
        score = r.get("score")
        if score is None:
            score = r.get('gradingResult', {}).get('score', 0)
        if score is None:
            score = 1.0 if r.get('success', False) else 0.0
            
        stats[p]["score_sum"] += float(score)

        if r.get("error"):
            stats[p]["error"] += 1
        elif r.get("success"):
            stats[p]["pass"] += 1
        else:
            stats[p]["fail"] += 1

    print(f"\n### Medium-Mode Results: {provider.upper()}")
    print("| Model | Pass | Fail | Error | Avg Score |")
    print("|-------|------|------|-------|-----------|")

    model_names = []
    avg_scores = []
    for model, counts in stats.items():
        avg_score = (counts["score_sum"] / counts["total"]) * 100 if counts["total"] > 0 else 0
        model_short = model.split("/")[-1]
        print(f"| {model_short} | {counts['pass']} | {counts['fail']} | {counts['error']} | {avg_score:.1f}% |")
        model_names.append(model_short)
        avg_scores.append(avg_score)
        
    plt.figure(figsize=(8, 5))
    bars = plt.bar(model_names, avg_scores, color=['#4C72B0', '#55A868', '#C44E52'])
    plt.xlabel('Model')
    plt.ylabel('Average Score (%)')
    plt.title(f'{provider.upper()} Vulnerability Detection - Medium Mode')
    plt.ylim(0, 100)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval:.1f}%', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(f"benchmark_results_medium_{provider}.png")
    print(f"Generated benchmark_results_medium_{provider}.png")
