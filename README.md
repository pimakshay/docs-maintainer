# Documentation Maintainer

Documentation Maintainer is an AI-powered system for reviewing, updating, and managing technical documentation. It combines a modern web frontend with an intelligent backend to streamline the process of keeping documentation accurate and up-to-date.

---

## Overview

- **Natural Language Querying**: Ask questions or describe changes in plain English to find relevant documentation sections.
- **AI Suggestions**: Receive suggested edits, additions, or removals powered by large language models (LLMs).
- **Review Workflow**: Approve, reject, or edit AI-generated suggestions before saving changes.
- **Modern UI**: Clean, responsive interface for efficient review and collaboration.

---

## Architecture

- **Frontend**: Built with Next.js and React, providing a side-by-side diff view, markdown rendering, and intuitive controls. See [Frontend README](./nextjs_frontend/FRONTEND_README.md) for details.
- **Backend**: FastAPI-based service orchestrating a Retrieval-Augmented Generation (RAG) pipeline using LangChain, ChromaDB, and Pydantic. See [Backend README](./fastapi_backend/BACKEND_README.md) for details.
- **Data Storage**: Uses ChromaDB to store document chunks and embeddings. See [Data Storage and Retrieval](./docs/data_storage_and_retrieval.md).

### Backend Architecture Diagram

![Backend Architecture](docs/assets/BackendArchitecture.png)

The diagram above illustrates the core components of the backend system:

- **FastAPI Application**: Serves as the main entry point, handling API requests from the frontend.
- **RAG Pipeline**: Implements Retrieval-Augmented Generation using LangChain to find and process relevant documentation chunks.
- **ChromaDB**: Stores document embeddings and metadata, enabling efficient semantic search and retrieval.
- **LLM Integration**: Connects to large language models (OpenAI or Google) to generate suggestions and edits based on user queries.
- **Pydantic Models**: Used for data validation and structured responses throughout the API.

This architecture enables scalable, intelligent document management and seamless integration with the modern frontend.


---

## Key Features

- **Query → Suggest → Review → Save**: Enter a query, get relevant docs and AI suggestions, review changes, and update documentation.
- **Diff Highlighting**: Visualize changes with color-coded badges and markdown support.
- **Flexible Embeddings**: Supports Google and OpenAI embedding models for document retrieval.
- **Evaluation Methods**: Includes ground-truth, unit, negative, and human-in-the-loop testing. See [Framework Evaluation](./docs/framework_eval_methods.md).

---

## Getting Started

1. **Install [uv](https://github.com/astral-sh/uv) (recommended):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Install dependencies:**
   ```bash
   uv sync
   ```
3. **Documentation Markdown Files**
   - place the markdown files inside: `data/documentation/`
3. **Set up environment variables:**
   - Copy `.env.example` to `.env` in `fastapi_backend/` and fill in required keys.
   - Input `DOC_DIR_PATH` as `data/documentation` in `.env`

4. **Run the backend:**
   ```bash
   cd fastapi_backend
   uvicorn routes:app --host 0.0.0.0--reload
   ```
5. **Run the frontend:**
   ```bash
   cd nextjs_frontend
   npm install
   npm run dev
   ```

See [Deployment and Scaling](./docs/deployment_and_scaling.md) for more.

---

## Documentation

- [Frontend Guide](./nextjs_frontend/FRONTEND_README.md)
- [Backend Guide](./fastapi_backend/BACKEND_README.md)
- [Data Storage & Retrieval](./docs/data_storage_and_retrieval.md)
- [Framework Evaluation](./docs/framework_eval_methods.md)
- [Deployment & Scaling](./docs/deployment_and_scaling.md)