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

# define LLM manager
llm_manager = LLMManager(api_key=settings.GOOGLE_API_KEY,
                        llm_model_name=settings.GEMINI_MODEL_NAME, 
                        embedding_model_name=settings.GEMINI_EMBEDDING_MODEL_NAME)

# define rag pipeline
rag_pipeline = VanillaRAGPipeline(llm_manager=llm_manager, 
                                  doc_dir_path=settings.DOC_DIR_PATH,
                                  top_k_docs=settings.TOP_K_DOCS,
                                  chunk_size=settings.CHUNK_SIZE,
                                  chunk_overlap=settings.CHUNK_OVERLAP,
                                  chroma_persist_dir=settings.CHROMA_DB_NAME                                
                                  )
qa_model = rag_pipeline.setup_qa_chain()


def suggest_changes(query: str, docs: List[Document]):
    """
    Suggests changes to a list of documents based on a user query.

    Args:
        query (str): The user's query string.
        docs (List[Document]): A list of documents with their similarity scores.

    Returns:
        List[DocumentUpdate]: Suggested changes for each relevant document.
    """
    system_prompt = diff_suggestion_prompt.system_prompt
    change_suggestions = []

    for doc in docs:
        score = doc[1]
        doc = doc[0]
        if score > settings.SCORE_THRESHOLD:
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
    """
    Retrieve relevant documents for a given query and suggest possible changes.

    Args:
        query (str): The user's query string.

    Returns:
        List[DocumentUpdate]: A list of suggested changes for the most relevant documents.
    """
    found_docs = rag_pipeline.docSearch.similarity_search_with_score(query,
                                                                    k=settings.TOP_K_DOCS)

    suggested_changes = suggest_changes(query, found_docs)

    return suggested_changes

if __name__ == "__main__":
    uvicorn.run("routes:app", port=5000, log_level="info", reload=True)