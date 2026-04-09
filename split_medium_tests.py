import csv
import os

input_csv = "tests_hard.csv"
providers = ["aws", "azure", "gcp", "oracle"] # Terragoat has oracle/alicloud, we group oracle or alicloud into oracle/others if requested

with open(input_csv, 'r', encoding='utf-8') as f:
    reader = list(csv.reader(f))
    header = reader[0]
    rows = reader[1:]

for p in providers:
    out_csv = f"tests_medium_{p}.csv"
    p_rows = [r for r in rows if f"/{p}/" in r[0]]
    if p == "oracle":
        # Group alicloud into oracle if explicitly trying to test it, or just use both
        p_rows = [r for r in rows if "/oracle/" in r[0] or "/alicloud/" in r[0]]
        
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(p_rows)
    print(f"Generated {out_csv} with {len(p_rows)} files.")
