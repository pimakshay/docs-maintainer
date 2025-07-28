from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from langchain.schema import Document
from numpy import diff
import uvicorn

from config import settings
from helpers.prompts.diff_suggestion_prompt import system_prompt
from helpers.llm_manager import LLMManager
from helpers.prompts import diff_suggestion_prompt
from pipelines.vanilla_rag_pipeline import VanillaRAGPipeline
from models import ModelOutput, DocumentMetadata, DocumentUpdate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# print("Debugging...")
# print("GOOGLE_API_KEY:", settings.GOOGLE_API_KEY)
# print("GEMINI_MODEL_NAME:", settings.GEMINI_MODEL_NAME)
# print("GEMINI_EMBEDDING_MODEL_NAME:", settings.GEMINI_EMBEDDING_MODEL_NAME)
# print("FRONTEND_URL:", settings.FRONTEND_URL)
import os
from dotenv import load_dotenv

load_dotenv(".env")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")
GEMINI_EMBEDDING_MODEL_NAME = os.getenv("GEMINI_EMBEDDING_MODEL_NAME")

# define LLM manager
llm_manager = LLMManager(api_key=GOOGLE_API_KEY,
                        llm_model_name=GEMINI_MODEL_NAME, 
                        embedding_model_name=GEMINI_EMBEDDING_MODEL_NAME)

# define rag pipeline
doc_dir_path = "/home/akshay/Documents/projects/pluno_tasks/documentation_openai_sdk/47b65859-969e-4294-9cc4-078d6bf705c9"
rag_pipeline = VanillaRAGPipeline(llm_manager=llm_manager, 
                                  doc_dir_path=doc_dir_path)
qa_model = rag_pipeline.setup_qa_chain()


def suggest_changes(query: str, docs: List[Document]):
    system_prompt = diff_suggestion_prompt.system_prompt
    change_suggestions = []

    for doc in docs:
        score = doc[1]
        doc = doc[0]
        if score > 0.4:
            continue

        user_prompt = diff_suggestion_prompt.create_user_prompt(query, doc.page_content, doc.metadata["title"])
        
        changes_identifier = llm_manager.llm_model.with_structured_output(ModelOutput)
        selected_method = changes_identifier.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        document_metadata = DocumentMetadata(
                            title=doc.metadata["title"],
                            source_url=doc.metadata["source_url"],
                            file_path=doc.metadata["file_path"]
                        )
        document_update = DocumentUpdate(
                            model_output=selected_method,
                            document_metadata=document_metadata
                        )
        change_suggestions.append(document_update)

    return change_suggestions

@app.post("/retrieve_relevant_documents")
def retrieve_relevant_documents(query: str):
    found_docs = rag_pipeline.docSearch.similarity_search_with_score(query,k=5)

    suggested_changes = suggest_changes(query, found_docs)


    return suggested_changes

if __name__ == "__main__":
    uvicorn.run("routes:app", port=5000, log_level="info", reload=True)