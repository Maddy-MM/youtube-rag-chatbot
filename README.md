# YouTube RAG Chatbot

A **Retrieval-Augmented Generation (RAG) system** that allows users to ask questions about any YouTube video using its transcript. The system processes video transcripts, converts them into embeddings, retrieves relevant context, and generates accurate answers using a Large Language Model.

---

## Table of Contents

1. Overview
2. Features
3. Project Workflow
4. RAG Pipeline Architecture
5. API Endpoints
6. Frontend (Streamlit UI)
7. Project Structure
8. Installation & Setup
9. How to Run
10. System Design Decisions
11. Limitations
12. Future Improvements
13. Tech Stack

---

## Overview

This project demonstrates an **end-to-end GenAI system** that combines:

* Transcript extraction from YouTube videos
* Semantic search using vector embeddings
* Context-aware answer generation using LLMs
* Backend API with FastAPI
* Interactive UI using Streamlit
* Containerization with Docker

The system ensures that answers are **grounded strictly in the video content**, reducing hallucinations and improving reliability.

---

## Features

* Ask questions about any YouTube video
* Transcript-based contextual answering (no hallucination outside context)
* Automatic transcript extraction with fallback handling
* Semantic search using FAISS vector database
* HuggingFace embeddings for efficient retrieval
* LLM-powered answer generation
* Clean Streamlit chat interface
* FastAPI backend for scalable API design
* Docker-ready for deployment

---

## Project Workflow

1. User provides a YouTube video URL
2. Extract video ID
3. Fetch transcript using YouTube API
4. Split transcript into chunks
5. Convert chunks into embeddings
6. Store embeddings in FAISS vector database
7. Retrieve relevant chunks for a query
8. Pass context + question to LLM
9. Generate and return answer

---

## RAG Pipeline Architecture

### 1. Transcript Extraction

* Uses `youtube-transcript-api`
* Attempts English transcript first
* Falls back to available language
* Handles missing transcripts gracefully

---

### 2. Text Splitting

* Uses `RecursiveCharacterTextSplitter`
* Chunk size: 1000
* Overlap: 200
* Ensures semantic continuity between chunks

---

### 3. Embeddings

* Model: `sentence-transformers/all-MiniLM-L6-v2`
* Converts text chunks into dense vectors
* Optimized for semantic similarity

---

### 4. Vector Store

* FAISS (Facebook AI Similarity Search)
* Stores embeddings for fast retrieval
* In-memory caching for processed videos

---

### 5. Retriever

* Similarity-based retrieval
* Top-k results: `k = 4`
* Fetches most relevant transcript chunks

---

### 6. LLM Chain

* Model: `openai/gpt-oss-20b` via HuggingFace

* Prompt constraints:

  * Answer only from context
  * Say “I don’t know” if insufficient context

* Built using LangChain:

  * `RunnableParallel`
  * `PromptTemplate`
  * `StrOutputParser`

---

## API Endpoints

### Process Video

* `POST /process_video`
* Input:

  ```json
  {
    "video_id": "youtube_url_or_id"
  }
  ```
* Function:

  * Extract transcript
  * Create embeddings
  * Store vector database

---

### Ask Question

* `POST /ask`
* Input:

  ```json
  {
    "video_id": "youtube_url_or_id",
    "question": "Your question here"
  }
  ```
* Returns:

  * Context-aware answer

---

## Frontend (Streamlit UI)

The Streamlit interface provides:

* Video input screen
* Processing feedback
* Interactive chat interface
* Message history tracking
* Clean modern UI with sidebar explanation

### User Flow

1. Paste YouTube link
2. Click **Process Video**
3. View video preview
4. Start chatting
5. Ask questions / summaries / insights

---

## Project Structure

```
youtube-rag-chatbot/  

├── api/
│   └── routes.py  

├── src/
│   ├── ingest.py  
│   ├── splitter.py  
│   ├── embeddings.py  
│   ├── retriever.py  
│   ├── chains.py  

├── notebooks/
│   └── experimentation.ipynb  

├── app.py                # Streamlit UI  
├── main.py               # FastAPI backend  
├── requirements.txt  
├── requirements_streamlit.txt  
├── .env  
├── Dockerfile  
```

---

## Installation & Setup

### 1. Clone Repository

```
git clone https://github.com/<your-username>/youtube-rag-chatbot.git
cd youtube-rag-chatbot
```

---

### 2. Create Virtual Environment

```
python -m venv venv

# macOS/Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate  
```

---

### 3. Install Dependencies

Backend:

```
pip install -r requirements.txt
```

Frontend:

```
pip install -r requirements_streamlit.txt
```

---

## How to Run

### Run Backend (FastAPI)

```
uvicorn main:app --reload
```

API will be available at:

```
http://127.0.0.1:8000
```

---

### Run Frontend (Streamlit)

```
streamlit run app.py
```

---

## System Design Decisions

### In-Memory Vector Store

* Uses dictionary-based caching:

  ```
  vector_store_cache = {}
  ```
* Avoids recomputation for already processed videos
* Faster response time for repeated queries

---

### Stateless API Design

* Each request independently retrieves vector store
* Ensures modular and scalable architecture

---

### Prompt Engineering

* Strict grounding:

  * Prevents hallucinations
  * Improves trustworthiness

---

## Limitations

* No persistent storage (data lost on restart)
* No Redis caching (yet)
* Depends on transcript availability
* Single-user in-memory design
* No authentication or rate limiting

---

## Future Improvements

* Redis-based caching for scalability
* Persistent vector database (Chroma / Pinecone)
* Multi-video querying support
* Streaming responses for better UX
* Authentication and rate limiting
* Deployment on cloud (Render / AWS)
* UI improvements (history, saved chats)

---

## Tech Stack

### Languages & Libraries

* Python
* LangChain
* HuggingFace Transformers
* Sentence Transformers

### Backend

* FastAPI

### Vector Database

* FAISS

### Frontend

* Streamlit

### Deployment

* Docker

