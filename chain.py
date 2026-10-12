import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

rewrite_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a medical coding assistant. Rewrite the user's plain-language "
        "description into standard clinical terminology suitable for searching "
        "ICD-10-CM code descriptions. Reply with only the clinical terms on one "
        "line. Do not add explanations, and do not give codes.",
    ),
    ("human", "{description}"),
])

rewrite_chain = rewrite_prompt | llm | StrOutputParser()


def rewrite_to_clinical_terms(description):
    return rewrite_chain.invoke({"description": description}).strip()


if __name__ == "__main__":
    text = "my blood sugar is always high and I have type 2 diabetes with kidney problems"
    print(rewrite_to_clinical_terms(text))