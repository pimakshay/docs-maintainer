import warnings
import os
import json
from uuid import uuid4
from typing import List, Dict, Any, Tuple

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.text_splitter import Language
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever


from fastapi_backend.helpers.document_cleaner import DocumentCleaner
from fastapi_backend.helpers.llm_manager import LLMManager
from fastapi_backend.helpers.query_transformation import QueryTransformer



class HybridRAGPipeline:
    def __init__(self, 
                llm_manager:LLMManager=None, 
                doc_dir_path:str=None,
                chroma_persist_dir: str="chroma_recursive_markdown",
                top_k_docs: int = 5,
                chunk_size: int = 1000,
                chunk_overlap: int = 0,
                enable_query_preprocessing: bool = True,
                enable_document_cleaning: bool = True,
                ):
        warnings.filterwarnings("ignore")
        # get all filenames inside doc_dir_paths
        self.file_paths = []
        if doc_dir_path:
            for root, dirs, files in os.walk(doc_dir_path):
                for file in files:
                    if file.endswith('.json'):
                        self.file_paths.append(os.path.join(root, file))
        
        self.documents = None
        self.filtered_docs = []
        self.chromadbDocSearch = None
        self.llm_model = llm_manager.llm_model if llm_manager else None
        self.embedding_model = llm_manager.embeddings if llm_manager else None
        self.qa = None

        # retrieval parameters
        self.top_k_docs = top_k_docs
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chroma_db_dir = chroma_persist_dir
        self.query_preprocessor=QueryTransformer(llm_manager=llm_manager) if enable_query_preprocessing else None
        self.document_cleaner = DocumentCleaner(llm_manager=llm_manager) if enable_document_cleaning else None



    def preprocess_query(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Preprocess the user query to improve retrieval.
        """
        if self.query_preprocessor:
            improved_query = self.query_preprocessor.improve_query_with_llm(
                query=query,
            )
            return improved_query
        else:
            return query


    def load_documents(self):
        documents = []
        cleaning_stats = {
            'total_documents': 0,
            'cleaned_documents': 0,
            'total_reduction_percentage': 0,
        }
        for file_path in self.file_paths:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    
                    data = json.load(f)
                    markdown = data.get("markdown", "")
                    metadata = data.get("metadata", {})

                    # Load only english language documents
                    if metadata.get("language", "") != "en":
                        continue

                    cleaning_stats['total_documents'] += 1

                    # apply document cleaning
                    if self.document_cleaner:
                        cleaned_content, cleaning_info = self.document_cleaner.clean_document(
                            markdown, 
                            use_llm=True
                        )
                        
                        if cleaning_info['reduction_percentage'] > 0:
                            cleaning_stats['cleaned_documents'] += 1
                            cleaning_stats['total_reduction_percentage'] += cleaning_info['reduction_percentage']
                        
                        # Update metadata with cleaning info
                        metadata['cleaning_info'] = cleaning_info
                        markdown = cleaned_content
                    else:
                        markdown = markdown                        

                    title = metadata.get("title", "")
                    source_url = metadata.get("sourceURL", "")
                    scrape_id = metadata.get("scrapeId", "")

                    doc = Document(
                        page_content=markdown,
                        metadata={
                            "title": title,
                            "source_url": source_url,
                            "file_path": file_path,  # helpful for debugging
                            "scrape_id": scrape_id
                        },
                        id=str(uuid4())
                    )
                    documents.append(doc)
            else:
                raise ValueError(f"Unsupported file format: {file_path}. Only JSON files are supported.")
             

        self.documents = documents
        return documents

    def setup_bm25_vector_store(self, collection_name="default_collection"):
        pass

    def setup_chromadb_vector_store(self, collection_name="default_collection"):
        if self.embedding_model is None:
            raise ValueError("Embedding model is not set")
        
        if not os.path.exists(self.chroma_db_dir):
            os.makedirs(self.chroma_db_dir)

        persist_dir = self.chroma_db_dir

        chroma_db_path = os.path.join(persist_dir, "chroma.sqlite3")

        print("Chroma DB path:", chroma_db_path)
        print("Collection name:", collection_name)
        print("Persist directory:", persist_dir)


        # Check if the DB already exists
        if os.path.exists(chroma_db_path):
            print("Loading existing Chroma DB...")
            self.chromadbDocSearch = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_model,
                persist_directory=persist_dir
            )
            
            # Load existing documents from the DB to populate filtered_docs for BM25
            print("Loading existing documents from Chroma DB for BM25 retriever...")
            # Get all documents from the existing collection
            all_docs = self.chromadbDocSearch.get()
            if all_docs and 'ids' in all_docs:
                # Retrieve the actual document content using the IDs
                self.filtered_docs = []
                for doc_id in all_docs['ids']:
                    doc = self.chromadbDocSearch.get(ids=[doc_id])
                    if doc and 'documents' in doc and doc['documents']:
                        # Create Document objects with the retrieved content
                        content = doc['documents'][0]
                        metadata = doc['metadatas'][0] if doc['metadatas'] else {}
                        document = Document(
                            page_content=content,
                            metadata=metadata,
                            id=doc_id
                        )
                        self.filtered_docs.append(document)
                print(f"Loaded {len(self.filtered_docs)} existing documents from Chroma DB")
            else:
                print("No existing documents found in Chroma DB")
                self.filtered_docs = []

        else:
            print("Creating new Chroma DB...")
            documents = self.load_documents()
            text_splitter = RecursiveCharacterTextSplitter.from_language(
                chunk_size=1000,
                chunk_overlap=0,
                language=Language.MARKDOWN,
            )
            split_docs = text_splitter.split_documents(documents)

            # filtered_docs = [doc for doc in split_docs if len(doc.page_content.strip()) >= 100]
            for chunk in split_docs:
                if len(chunk.page_content.strip()) < 100:
                    continue

                # Create a unique ID for the chunk
                chunk_id = str(uuid4())

                # Add/Update metadata to include original and chunk IDs
                new_metadata = dict(chunk.metadata)
                # new_metadata["scrape_id"] = original_id  # original document id
                new_metadata["chunk_id"] = chunk_id      # unique chunk id

                # Replace metadata with new metadata
                chunk.metadata = new_metadata

                self.filtered_docs.append(chunk)            

            print(f"Total split docs before filtering: {len(split_docs)}")
            print(f"Total split docs after filtering: {len(self.filtered_docs)}")
            
            self.chromadbDocSearch = Chroma.from_documents(
                self.filtered_docs, 
                self.embedding_model, 
                collection_name=collection_name,
                persist_directory=persist_dir
            )

        return self.chromadbDocSearch, self.filtered_docs



    def retrieve_documents(self, query: str, use_preprocessing: bool = True) -> Tuple[List[Tuple[Document, float]], Dict[str, Any]]:
        """
        Retrieve relevant documents with optional query preprocessing.
        """
        retrieval_info = {
            'original_query': query,
            'query_transformation_applied': False,
            'preprocessing_info': {},
            'retrieval_metrics': {}
        }
        
        # Preprocess query if enabled
        if use_preprocessing and self.query_preprocessor:
            improved_query = self.preprocess_query(query)
            retrieval_info['query_transformation_applied'] = True
            retrieval_info['improved_query'] = improved_query
            query = improved_query
        
        if self.documents is None:
            self.load_documents()

        # Perform retrieval
        if not self.chromadbDocSearch:
            self.setup_chromadb_vector_store()
            # NOTE: not called--> self.setup_bm25_vector_store()


        retriever_chromadb = self.chromadbDocSearch.as_retriever(search_kwargs={"k": self.top_k_docs})
        bm25_retriever = BM25Retriever.from_documents(documents=self.filtered_docs)
        bm25_retriever.k = self.top_k_docs


        # Initialize the ensemble retriever
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever_chromadb],
                                       weights=[0.4, 0.6])

        found_docs = ensemble_retriever.get_relevant_documents(query=query)
        
        # print(found_docs)
        # Add retrieval metrics
        retrieval_info['retrieval_metrics'] = {
            'total_docs_retrieved': len(found_docs),
            # 'avg_score': sum(score for _, score in found_docs) / len(found_docs) if found_docs else 0,
            # 'min_score': min(score for _, score in found_docs) if found_docs else 0,
            # 'max_score': max(score for _, score in found_docs) if found_docs else 0
        }
        
        return found_docs, retrieval_info
