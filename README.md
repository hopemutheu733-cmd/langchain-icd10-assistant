# ICD-10 Assistant (LangChain + Python + MySQL)

A small API that turns a plain-language description into suggested ICD-10-CM codes. It's a code-first rebuild of my [n8n version](https://github.com/hopemutheu733-cmd/n8n-icd10-assistant), using LangChain, FastAPI and MySQL instead of n8n and Supabase.

## How it works

1. **Rewrite**: an LLM rewrites the user's description into clinical terminology.
2. **Search**: MySQL full-text search finds up to 25 candidate codes from the CMS ICD-10-CM list.
3. **Pick**: a second LLM chooses up to 3 codes from those candidates only, with a short reason for each.
4. **Validate**: every chosen code is checked against the database, and any code that doesn't exist is dropped.

Letting the model choose only from real candidates, and validating the result, guards against hallucinated codes.

The database holds 74,879 ICD-10-CM codes loaded from the CMS code file.

## Example

![API demo](demo.png)

`POST /suggest`

```json
{ "description": "my blood sugar is always high and I have type 2 diabetes with kidney problems" }
```

Response:

```json
{
  "clinical_terms": "Type 2 diabetes mellitus with diabetic nephropathy and persistent hyperglycemia",
  "suggestions": [
    { "code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "reason": "Matches type 2 diabetes and high blood sugar" },
    { "code": "E11.21", "description": "Type 2 diabetes mellitus with diabetic nephropathy", "reason": "Matches type 2 diabetes and kidney problems" }
  ]
}
```

An empty description returns a `400` error.

## Setup

1. Create and activate a virtual environment, then run `pip install -r requirements.txt`.
2. Run `schema.sql` in MySQL to create the database and table.
3. Convert the CMS ICD-10-CM codes file to a CSV with two columns, `code` and `description`, and import it into the `icd10_codes` table (the converter script in my n8n project's repo does this).
4. Copy `.env.example` to `.env` and fill in your MySQL details and your OpenRouter key and model.
5. Start the API with `uvicorn api:app --reload`, then open `http://127.0.0.1:8000/docs` to try it.

## Files

- `db.py`: MySQL connection and full-text search
- `chain.py`: LangChain setup and the rewrite step
- `pipeline.py`: the pick step, validation and the full flow
- `api.py`: the FastAPI endpoint

## Notes and limits

- MySQL full-text search ignores very short words like "2", so type 1 and type 2 diabetes codes can appear together in the candidates. The pick step resolves this.
- Free OpenRouter models can hit rate limits.
- This is a learning project. Suggestions are not a substitute for a trained medical coder.

Built by Hope Mutheu.