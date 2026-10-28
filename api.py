from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from pipeline import suggest_codes

app = FastAPI(title="ICD-10 Assistant")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(Path(__file__).parent / "index.html")


class DescriptionRequest(BaseModel):
    description: str = ""


def format_code(code):
    if len(code) > 3 and "." not in code:
        return code[:3] + "." + code[3:]
    return code


@app.post("/suggest")
def suggest(request: DescriptionRequest):
    result = suggest_codes(request.description)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    for item in result.get("suggestions", []):
        item["code"] = format_code(item["code"])
    return result