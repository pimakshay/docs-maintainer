from calendar import c
import warnings
import os
import json
from uuid import uuid4
from typing import List, Dict, Any, Tuple

from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.text_splitter import Language

from fastapi_backend.helpers.llm_manager import LLMManager
from fastapi_backend.helpers.query_transformation import QueryTransformer
from fastapi_backend.helpers.document_cleaner import DocumentCleaner




class VanillaRAGPipeline:
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
        self.docSearch = None
        self.llm_model = llm_manager.llm_model if llm_manager else None
        self.embedding_model = llm_manager.embeddings if llm_manager else None
        self.qa = None

        # retrieval parameters
        self.top_k_docs = top_k_docs
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chroma_db_dir = chroma_persist_dir
        self.query_preprocessor=QueryTransformer(llm_manager=llm_manager) if enable_query_preprocessing else None


    


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
        
        # print("Debugging...")
        # for i, doc in enumerate(documents):
        #     print(f"\nRaw Document {i+1}:")
        #     print(f"Length: {len(doc.page_content)} characters")
        #     # print(f"Content:\n{doc.page_content}")
        #     print(f"Metadata: {doc.metadata}")        

        self.documents = documents
        return documents

    def setup_vector_store(self, collection_name="default_collection"):
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
            self.docSearch = Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_model,
                persist_directory=persist_dir
            )
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
            filtered_docs = []
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

                filtered_docs.append(chunk)            

            print(f"Total split docs before filtering: {len(split_docs)}")
            print(f"Total split docs after filtering: {len(filtered_docs)}")
            
            self.docSearch = Chroma.from_documents(
                filtered_docs, 
                self.embedding_model, 
                collection_name=collection_name,
                persist_directory=persist_dir
            )

        return self.docSearch



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


        found_docs = retriever_chromadb.get_relevant_documents(query=query)
        
        # print(found_docs)
        # Add retrieval metrics
        retrieval_info['retrieval_metrics'] = {
            'total_docs_retrieved': len(found_docs),
            # 'avg_score': sum(score for _, score in found_docs) / len(found_docs) if found_docs else 0,
            # 'min_score': min(score for _, score in found_docs) if found_docs else 0,
            # 'max_score': max(score for _, score in found_docs) if found_docs else 0
        }
        
        return found_docs, retrieval_info

    
    def setup_qa_chain(self):
        """
        User can interact with the documentation and get a summarized response.
        In the current implementation, we haven't used qa chain. 
        It can be easily incorporated by using a query classifier which decides if the query is about document retrieval or summarization.
        """
        if self.llm_model is None:
            raise ValueError("LLM model is not set")
        if self.docSearch is None:
            self.setup_vector_store()
        
        qa = RetrievalQA.from_chain_type(
            llm=self.llm_model,
            chain_type="stuff",
            retriever=self.docSearch.as_retriever(),
            return_source_documents=True
        )
        self.qa = qa
        return qa