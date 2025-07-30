# Data Storage and Retrieval

This document outlines how **Documentation Maintainer** stores and retrieves data to support intelligent document review and update workflows.

We use **[ChromaDB](https://www.trychroma.com/)** as the underlying vector store for storing documentation chunks and their semantic embeddings, enabling efficient retrieval for downstream AI tasks.

---

## 2. Vector Storage

ChromaDB stores document embeddings as high-dimensional vectors in a specialized **Approximate Nearest Neighbor (ANN)** index. The actual vectors are not stored in the main SQLite database (`chromadb.sqlite3`), but in optimized binary index files (e.g., `index.faiss`), located in the configured `persist_directory`.

* **Metadata**, such as document source and chunk information, is stored in the SQLite database.
* **Embeddings** are stored and indexed separately for performance.

---

## 3. Embedding Models

Embeddings convert document chunks and queries into vectors that capture semantic meaning.

Currently supported embedding backends:

* 🔹 **Google Embedding Model** (e.g., `models/text-embedding-004`)
* 🔹 **OpenAI Embedding Model** (e.g., `text-embedding-3-small`)


Model choice impacts both retrieval quality and cost/performance tradeoffs.

---

## 4. Distance Metrics and Search Algorithms

We mainly use **cosine similarity** for retrieval techniques but there are other alternatives:

* **Cosine Similarity** (default): Measures angle between vectors, ideal for high-dimensional text embeddings.
* **Euclidean Distance (L2)**: Measures straight-line distance between vectors; less common in semantic text search.
* **Maximum Marginal Relevance (MMR)**: Balances **relevance** and **diversity** in results to avoid redundancy in retrieved chunks.

---

## 5. Design Choices

To improve retrieval quality and minimize noise:

* **Discarded short documents**: Chunks with fewer than **100 characters** are excluded from indexing to reduce irrelevant matches.
* **No chunk overlap**: We avoid overlapping chunks (`chunk_overlap = 0`) to reduce repetition in retrieval results and prevent the AI from being shown duplicate or overly similar text.

---

## 6. Future Improvements

Planned enhancements to retrieval include:

* Support for **hybrid search** (BM25 + embeddings)
* Integration of **reranker models** (e.g., OpenAI Rerank)
* Embedding caching and monitoring for drift
