from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from langchain.schema import Document
import uvicorn

from fastapi_backend.config import settings
from fastapi_backend.helpers.prompts.diff_suggestion_prompt import system_prompt
from fastapi_backend.helpers.llm_manager import LLMManager
from fastapi_backend.helpers.prompts import diff_suggestion_prompt
from fastapi_backend.pipelines.vanilla_rag_pipeline import VanillaRAGPipeline
from fastapi_backend.pipelines.hybrid_rag_pipeline import HybridRAGPipeline
from fastapi_backend.models import ModelOutput, DocumentMetadata, DocumentUpdate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# define LLM manager
llm_manager = LLMManager(api_key=settings.API_KEY,
                        provider=settings.PROVIDER,
                        llm_model_name=settings.LLM_MODEL_NAME, 
                        embedding_model_name=settings.EMBEDDING_MODEL_NAME)

# define rag pipeline
if settings.RETRIEVAL_METHOD == "hybrid":
    print("Hybrid RAG pipeline selected")
    rag_pipeline = HybridRAGPipeline(llm_manager=llm_manager, 
                                    doc_dir_path=settings.DOC_DIR_PATH,
                                    top_k_docs=settings.TOP_K_DOCS,
                                    chunk_size=settings.CHUNK_SIZE,
                                    chunk_overlap=settings.CHUNK_OVERLAP,
                                    chroma_persist_dir=settings.CHROMA_DB_NAME                                
                                    )

elif settings.RETRIEVAL_METHOD == "vanilla":
    print("Vanilla RAG pipeline selected")
    rag_pipeline = VanillaRAGPipeline(llm_manager=llm_manager, 
                                    doc_dir_path=settings.DOC_DIR_PATH,
                                    top_k_docs=settings.TOP_K_DOCS,
                                    chunk_size=settings.CHUNK_SIZE,
                                    chunk_overlap=settings.CHUNK_OVERLAP,
                                    chroma_persist_dir=settings.CHROMA_DB_NAME                                
                                    )


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
        # score = doc[1]
        # doc = doc[0]
        # if score > settings.SCORE_THRESHOLD:
        #     continue

        user_prompt = diff_suggestion_prompt.create_user_prompt(query, doc.page_content, doc.metadata["title"])
        
        changes_identifier = llm_manager.llm_model.with_structured_output(ModelOutput)
        selected_method = changes_identifier.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ])

        document_metadata = DocumentMetadata(
                            original=doc.page_content,
                            chunk_id=doc.metadata["chunk_id"],
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
    found_docs, retrieval_info = rag_pipeline.retrieve_documents(query, use_preprocessing=True)

    print(f"Retrieval Info: {retrieval_info}")

    suggested_changes = suggest_changes(query, found_docs)

    return suggested_changes

@app.post("/apply_approved_changes")
def apply_approved_changes(docs: List[DocumentUpdate]):
    """
    Receives a list of approved document changes from the frontend
    and processes them.

    (Currently a placeholder implementation)
    """
    # TODO: Implement the logic to apply the changes.
    return f"Total approved documents: {len(docs)}"

@app.post("/chat")
def chat_with_documents(query: str, context_docs: List[str] = None):
    """
    Chat interface for asking questions about documents.
    
    Args:
        query (str): User's question
        context_docs (List[str], optional): Specific document content to use as context
        
    Returns:
        dict: Response containing answer and sources
    """
    # If no specific context provided, retrieve relevant documents
    if not context_docs:
        found_docs, retrieval_info = rag_pipeline.retrieve_documents(query, use_preprocessing=True)
        context_docs = [doc.page_content for doc in found_docs[:3]]  # Use top 3 docs
        sources = [{"title": doc.metadata.get("title", "Unknown"), 
                   "source_url": doc.metadata.get("source_url", "")} 
                  for doc in found_docs[:3]]
    else:
        sources = []
    
    # Create context from documents
    context = "\n\n".join(context_docs)
    
    # Create chat prompt
    chat_prompt = f"""Based on the following documentation context, please answer the user's question clearly and accurately.

Context:
{context}

User Question: {query}

Please provide a helpful answer based on the documentation provided. If the answer isn't in the context, please say so."""
    
    # Get response from LLM
    try:
        response = llm_manager.llm_model.invoke([
            {"role": "system", "content": "You are a helpful documentation assistant. Answer questions based on the provided context."},
            {"role": "user", "content": chat_prompt}
        ])
        
        return {
            "answer": response.content,
            "sources": sources,
            "query": query
        }
    except Exception as e:
        return {
            "answer": f"Sorry, I encountered an error: {str(e)}",
            "sources": [],
            "query": query
        }


# add a liveness check endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("routes:app", port=8000, log_level="info", reload=True)