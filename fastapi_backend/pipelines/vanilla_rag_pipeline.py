import warnings

from langchain.schema import Document

from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, MarkdownTextSplitter
from langchain.chains import RetrievalQA

from helpers.llm_manager import LLMManager
import os
import json


class VanillaRAGPipeline:
    def __init__(self, llm_manager:LLMManager=None, doc_dir_path:str=None):
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

    def load_documents(self):
        documents = []

        for file_path in self.file_paths:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    
                    data = json.load(f)
                    markdown = data.get("markdown", "")
                    metadata = data.get("metadata", {})

                    # Load only english language documents
                    if metadata.get("language", "") != "en":
                        continue

                    title = metadata.get("title", "")
                    source_url = metadata.get("sourceURL", "")
                    scrape_id = metadata.get("scrapeId", "")

                    doc = Document(
                        page_content=markdown,
                        metadata={
                            "title": title,
                            "source_url": source_url,
                            "file_path": file_path,  # helpful for debugging
                            # "scrape_id": scrape_id
                        }
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
        
        documents = self.load_documents()
        # text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_splitter = MarkdownTextSplitter(chunk_size=500, chunk_overlap=0)
        split_docs = text_splitter.split_documents(documents)

        filtered_docs = [doc for doc in split_docs if len(doc.page_content.strip()) >= 100]

        print(f"Total split docs before filtering: {len(split_docs)}")
        print(f"Total split docs after filtering: {len(filtered_docs)}")
        
        self.docSearch = Chroma.from_documents(
            filtered_docs, 
            self.embedding_model, 
            collection_name=collection_name,
            persist_directory="chroma"  # Directory to persist the vector store
        )
        return self.docSearch
    
    def setup_qa_chain(self):
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