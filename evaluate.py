"""Evaluate the live ICD-10 assistant on 20 plain-English test cases.

Run:  python evaluate.py
Needs: pip install requests

For each case, a result counts as a HIT if at least one acceptable code
appears among the suggestions. It counts as a TOP-1 HIT if the first
suggestion is an acceptable code.
"""
import csv
import time

import requests

API_URL = "https://langchain-icd10-assistant.onrender.com/suggest"
TIMEOUT = 180        # the free server can take about a minute to wake up
PAUSE_SECONDS = 3    # pause between calls to avoid LLM rate limits

# (plain-English description, acceptable codes)
# Check these against your ICD-10 reference before trusting the score.
CASES = [
    ("patient has high blood pressure", ["I10"]),
    ("type 2 diabetes with no complications", ["E11.9"]),
    ("type 2 diabetes with kidney disease", ["E11.21", "E11.22", "E11.29"]),
    ("migraine without aura", ["G43.009"]),
    ("acute bronchitis", ["J20.9"]),
    ("burning pain when passing urine and frequent urination", ["N39.0", "R30.0"]),
    ("low back pain", ["M54.50", "M54.59"]),
    ("asthma", ["J45.909"]),
    ("anaemia caused by iron deficiency", ["D50.9"]),
    ("pneumonia", ["J18.9"]),
    ("patient has a fever", ["R50.9"]),
    ("headache", ["R51.9"]),
    ("patient keeps vomiting", ["R11.10", "R11.2"]),
    ("acute appendicitis", ["K35.80", "K35.89"]),
    ("patient is depressed", ["F32.A", "F32.9"]),
    ("stomach acid coming back up into the throat (reflux)", ["K21.9"]),
    ("underactive thyroid", ["E03.9"]),
    ("malaria", ["B54", "B50.9"]),
    ("tuberculosis of the lung", ["A15.0"]),
    ("watery diarrhoea", ["R19.7", "A09"]),
]


def norm(code):
    return str(code).replace(".", "").strip().upper()


def call_api(description):
    for attempt in range(2):
        try:
            r = requests.post(API_URL, json={"description": description}, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            if attempt == 1:
                return {"error": str(e), "suggestions": []}
            time.sleep(10)


def main():
    rows = []
    hits = top1 = errors = 0
    for i, (desc, accepted) in enumerate(CASES, 1):
        data = call_api(desc)
        suggestions = [s.get("code", "") for s in data.get("suggestions", [])]
        accepted_n = {norm(c) for c in accepted}
        got_n = [norm(c) for c in suggestions]
        hit = any(c in accepted_n for c in got_n)
        first = bool(got_n) and got_n[0] in accepted_n
        if "error" in data:
            errors += 1
        hits += hit
        top1 += first
        print(f"{i:2d}. {'HIT ' if hit else 'MISS'} | {desc} | expected {accepted} | got {suggestions}")
        rows.append([i, desc, "/".join(accepted), "/".join(suggestions), hit, first])
        time.sleep(PAUSE_SECONDS)

    n = len(CASES)
    print()
    print(f"Acceptable code among suggestions: {hits} of {n}")
    print(f"First suggestion acceptable:       {top1} of {n}")
    if errors:
        print(f"Calls that errored (counted as misses): {errors}")

    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "description", "acceptable_codes", "suggested_codes", "hit", "first_is_hit"])
        w.writerows(rows)
    print("Saved results.csv")


if __name__ == "__main__":
    main()