import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from chain import llm, rewrite_to_clinical_terms
from db import get_connection, search_codes

pick_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a medical coding assistant. You are given a patient description "
        "and a list of candidate ICD-10-CM codes. Choose up to 3 codes from the "
        "candidate list that best match the description. Only use codes that "
        "appear in the candidate list. Never invent codes. Reply with only a "
        "JSON list, where each item has the keys \"code\" and \"reason\". The "
        "reason must be one short sentence. If no candidate fits, reply with an "
        "empty list [].",
    ),
    ("human", "Description: {description}\n\nCandidates:\n{candidates}"),
])

pick_chain = pick_prompt | llm | JsonOutputParser()


def validate_codes(picks):
    """Keep only codes that really exist in the database."""
    codes = [p.get("code", "").strip() for p in picks if isinstance(p, dict)]
    if not codes:
        return []
    placeholders = ", ".join(["%s"] * len(codes))
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT code, description FROM icd10_codes WHERE code IN ({placeholders})",
            codes,
        )
        valid = {row["code"]: row["description"] for row in cursor.fetchall()}
    finally:
        conn.close()

    results = []
    for p in picks:
        code = p.get("code", "").strip()
        if code in valid:
            results.append(
                {"code": code, "description": valid[code], "reason": p.get("reason", "")}
            )
    return results


def suggest_codes(description):
    description = (description or "").strip()
    if not description:
        return {"error": "Please enter a description."}

    clinical = rewrite_to_clinical_terms(description)
    candidates = search_codes(clinical, limit=25)
    if not candidates:
        return {"clinical_terms": clinical, "suggestions": []}

    candidate_text = "\n".join(f"{c['code']} - {c['description']}" for c in candidates)
    try:
        picks = pick_chain.invoke(
            {"description": description, "candidates": candidate_text}
        )
    except Exception as e:
        print("AI pick step failed:", e)
        picks = []
    if isinstance(picks, dict):
        picks = [picks]

    return {"clinical_terms": clinical, "suggestions": validate_codes(picks)}


if __name__ == "__main__":
    text = "my blood sugar is always high and I have type 2 diabetes with kidney problems"
    print(json.dumps(suggest_codes(text), indent=2))