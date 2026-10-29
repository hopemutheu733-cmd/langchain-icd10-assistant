# ICD-10 Assistant

Describe a patient's problem in plain English and get suggested ICD-10 diagnosis codes, each with a short reason.

**[Live demo](https://langchain-icd10-assistant.onrender.com)** · **[API docs](https://langchain-icd10-assistant.onrender.com/docs)**

> Hosted on a free plan, so the first load after a quiet period can take up to a minute while the server wakes up.

![Demo](demo.png)

## Overview

Medical coding is slow and detail-heavy. This project combines healthcare knowledge with AI to speed up the first step: finding the right code for a written clinical description.

Type "burning pain when passing urine" and it returns the clinical term **Dysuria** and the code **R30.0**, with a one-line reason.

This project is designed around a practical AI pattern: use a language model to interpret the problem, then ground the answer in a real ICD-10 database before suggesting a result.

## Why this project matters

Medical coding is a structured task, not open-ended chat. The model should not invent diagnoses or codes. Instead, it should:

- rewrite everyday wording into more clinical terminology
- search a trusted ICD-10 dataset for candidate matches
- select the strongest results from real codes
- explain each suggestion in plain language

This project demonstrates how AI can support healthcare workflows while staying grounded in real data.

## How it works

1. **Rewrite:** an LLM turns everyday wording into clinical terms.
2. **Search:** those terms query the ICD-10 table in MySQL for candidate codes.
3. **Pick:** the LLM chooses the best matches and explains each one.

Searching the database first keeps suggestions tied to real codes instead of letting the model invent them.

## Evaluation

I tested the system on 20 plain-English descriptions with known acceptable codes (`evaluate.py`, results in `results.csv`).

| Measure | Result |
| --- | --- |
| Acceptable code appeared in the suggestions | 16 of 20 (80%) |
| First suggestion was acceptable | 16 of 20 |

**Known failures:** empty results for "type 2 diabetes with kidney disease" and "fever", and over-specific picks for "pneumonia" and "headache".

This is a small sample of common conditions chosen by me, not a validated benchmark.

## Use the API

```bash
curl -X POST "https://langchain-icd10-assistant.onrender.com/suggest" \
  -H "Content-Type: application/json" \
  -d '{"description": "patient has chest pain and shortness of breath"}'
```

Example response:

```json
{
  "clinical_terms": "Chest pain; dyspnea",
  "suggestions": [
    {
      "code": "R07.9",
      "description": "Chest pain, unspecified",
      "reason": "Chest pain, unspecified matches the patient's chest pain without further specification."
    },
    {
      "code": "R06.00",
      "description": "Dyspnea, unspecified",
      "reason": "Dyspnea, unspecified matches the patient's shortness of breath."
    }
  ]
}
```

## Limitations and safety

- Suggestions are a starting point for a human coder, not a final answer. Not for clinical or billing use without review by a qualified coder.
- Do not enter real patient information. This is a demo, and requests are sent to a third-party LLM service.
- Search is keyword-based, so a query like "type 2 diabetes" can return Type 1 codes in the candidate list. The picking step corrects most of this, but not always.
- Covers ICD-10 diagnosis codes only, not procedure codes.

## Tech stack

Python · FastAPI · LangChain · OpenRouter · MySQL (Aiven) · HTML · Docker · Render

## Skills shown

- **AI/LLM engineering:** LangChain pipeline, prompt design, OpenRouter integration
- **Evaluation:** a 20-case test set, measured accuracy, documented failure cases
- **Backend:** REST API with FastAPI, request validation, MySQL queries
- **Frontend:** a single-page interface that calls the API
- **Deployment:** Docker, Render, managed cloud database, environment-based configuration
- **Practice:** secrets kept out of the repo, debugging from production logs
- **Domain knowledge:** ICD-10 coding and clinical terminology

## Project structure

```
.
├── index.html            # Web page served at /
├── api.py                # FastAPI app, home page, and /suggest endpoint
├── pipeline.py           # Rewrite, search, and pick steps
├── chain.py              # LLM setup and prompts
├── db.py                 # MySQL connection and code search
├── schema.sql            # Database table definitions
├── icd10.sql             # ICD-10 data to load into MySQL
├── evaluate.py           # Evaluation script
├── results.csv           # Evaluation output
├── Dockerfile            # Container build for deployment
├── .env.example          # Environment variable names
├── requirements.txt      # Python dependencies
├── README.md             # Project overview
├── demo.png              # Demo image
└── .gitignore
```

## Run it locally

```bash
git clone https://github.com/hopemutheu733-cmd/langchain-icd10-assistant.git
cd langchain-icd10-assistant
python -m pip install -r requirements.txt
```

Create a MySQL database, run `schema.sql`, then load `icd10.sql`. Copy `.env.example` to a new file named `.env` and fill it in:

```env
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PORT=3306
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=your_model_name
```

`OPENROUTER_MODEL` is any model ID from [openrouter.ai/models](https://openrouter.ai/models). Models ending in `:free` cost nothing but can be slower or busy.

Start the server:

```bash
python -m uvicorn api:app --reload
```

Then open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Docker and deployment

```bash
docker build -t icd10-assistant .
docker run -p 10000:10000 --env-file .env icd10-assistant
```

To deploy on Render:

1. Create a Web Service from this repo
2. Set Language to Docker
3. Add the environment variables above
4. Deploy

## Author

**Hope Mutheu** · [GitHub](https://github.com/hopemutheu733-cmd)
