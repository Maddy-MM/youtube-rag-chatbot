# YouTube RAG Chatbot

A **Retrieval-Augmented Generation (RAG) system** that allows users to ask questions about any YouTube video using its transcript. The system retrieves relevant context and generates grounded responses using a Large Language Model.

---

## Table of Contents

1. Overview
2. Features
3. Project Workflow
4. RAG Pipeline Architecture
5. API Endpoints
6. Frontend
7. Project Structure
8. Installation & Setup
9. How to Run
10. Deployment Architecture
11. Transcript Fetching Strategy
12. Limitations
13. Future Improvements
14. Tech Stack

---

## Overview

This project implements an **end-to-end GenAI pipeline** with a modular architecture:

* **FastAPI backend** handles the RAG pipeline
* **Streamlit frontend** provides an interactive chat interface
* Components are independently deployable

The system ensures responses remain **grounded in transcript data** to reduce hallucinations.

---

## Live Demo

* **Backend API:** [YouTube RAG Chatbot - Backend (Render)](https://your-backend.onrender.com)
* **Frontend:** [YouTube RAG Chatbot - Frontend (Streamlit)](https://your-frontend.streamlit.app)

> **Note:** The backend is hosted on Render's free tier and may take 30–60 seconds to wake up on the first request.

---

## Features

* Ask questions about any YouTube video
* Three-layer transcript fetching with graceful degradation
* Residential proxy support via Webshare for cloud IP bypass
* Manual transcript paste fallback when auto-fetch fails
* Context-aware responses based on transcripts
* Semantic search using FAISS
* HuggingFace embeddings for retrieval
* LLM-based answer generation
* Streamlit chat interface
* Modular API-based backend
* Docker support for deployment

---

## Project Workflow

1. User provides a YouTube video URL
2. Extract video ID
3. Attempt transcript fetch — direct, then proxy, then manual paste
4. Split transcript into chunks
5. Generate embeddings
6. Store embeddings in vector database
7. Retrieve relevant chunks based on user question
8. Pass context + query to LLM
9. Return generated response

---

## RAG Pipeline Architecture

### Transcript Extraction

* Uses `youtube-transcript-api` v1.2.4
* Three-layer fetching strategy (see Transcript Fetching Strategy section)
* Attempts English transcript first, falls back to any available language

### Text Splitting

* `RecursiveCharacterTextSplitter`
* Chunk size: 1000
* Overlap: 200

### Embeddings

* Model: `sentence-transformers/all-MiniLM-L6-v2`

### Vector Store

* FAISS for similarity search
* In-memory caching via `vector_store_cache` dictionary

### Retrieval

* Top-k similarity search (k = 4)

### LLM

* Model: `openai/gpt-oss-20b` (via HuggingFace Inference API)
* Constrained prompting to ensure grounded, transcript-based answers

---

## API Endpoints

### Process Video

`POST /process_video`
Attempts to fetch transcript automatically and builds vector store. Returns `{"error": "fallback"}` if both direct and proxy fetch fail, signalling the frontend to show the manual paste UI.

### Process Video Manual

`POST /process_video_manual`
Accepts a manually pasted transcript and runs it through the same pipeline as an auto-fetched transcript — split, embed, store. The `/ask` endpoint works identically regardless of how the transcript arrived.

### Ask Question

`POST /ask`
Returns context-aware answers based on retrieved transcript chunks.

---

## Frontend

Built with Streamlit:

* Video URL input
* Processing feedback with spinner
* Automatic transcript fetch with proxy fallback
* Manual transcript paste UI when auto-fetch fails
* Video thumbnail and title preview
* Chat interface with message history

### User Flow

1. Paste video link
2. Process video — auto-fetched or manually pasted transcript
3. Preview video thumbnail and title
4. Start chatting

---

## Project Structure

```text
youtube-rag-chatbot/

├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── src/
│   │   ├── ingest.py
│   │   ├── splitter.py
│   │   ├── embeddings.py
│   │   ├── retriever.py
│   │   └── chains.py
│   ├── api/
│   │   └── routes.py
│   └── .env
│
├── frontend/
│   ├── app.py
│   └── requirements.txt
│
└── README.md
```

---

## Installation & Setup

### Clone Repository

```bash
git clone https://github.com/<your-username>/youtube-rag-chatbot.git
cd youtube-rag-chatbot
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```ini
HUGGINGFACEHUB_API_TOKEN=your_token_here
HF_TOKEN=your_token_here

WEBSHARE_USER=your_webshare_username
WEBSHARE_PASS=your_webshare_password
```

> **Note:** Webshare credentials are only required for the proxy layer. The app works without them — it will fall back to the manual paste UI if both direct fetch and proxy fetch fail.

### Frontend Setup

```bash
cd ../frontend
pip install -r requirements.txt
```

---

## How to Run

### Backend

```bash
cd backend
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
streamlit run app.py
```

---

## Deployment Architecture

* Backend deployed as a Dockerized FastAPI service on Render
* Frontend deployed separately on Streamlit Community Cloud
* Communication via REST APIs
* Environment variables managed via Render dashboard and Streamlit secrets

---

## Transcript Fetching Strategy

YouTube blocks transcript fetch requests from cloud server IPs (Render, Streamlit Cloud, AWS, GCP, etc.) because they originate from well-known datacenter IP ranges. This required building a robust three-layer fetching strategy with graceful degradation.

### Layer 1 — Direct Fetch

The system first attempts a direct fetch using `youtube-transcript-api` with no proxy. This works reliably in local environments and occasionally succeeds on cloud too depending on YouTube's current blocklist state.

### Layer 2 — Residential Proxy via Webshare

If the direct fetch fails, the system retries using a Webshare residential proxy configured via the v1.2.4 `WebshareProxyConfig` API, passed into the `YouTubeTranscriptApi` constructor. A 3-second timeout is enforced on the proxy session to prevent long waits when the proxy itself is rate limited by YouTube.

> **Note on the free tier:** Webshare's free tier provides shared datacenter proxies, not true residential proxies. These get blocked by YouTube just like regular cloud IPs. In production, a paid Webshare residential proxy plan would make this layer fully reliable.

### Layer 3 — Manual Transcript Paste

If both fetch attempts fail, the backend returns `{"error": "fallback"}` and the frontend shows a manual paste UI directing the user to [youtubetranscript.com](https://youtubetranscript.com). The pasted transcript is submitted to a separate `/process_video_manual` endpoint and passed through the identical pipeline — split, embed, store — so the chat experience is unchanged.

### Why This Architecture

Several alternative approaches were evaluated before arriving at this design:

* **Client-side fetching on Streamlit** — worked initially but Streamlit Community Cloud IPs eventually got blocklisted too
* **Cloudflare Workers** — viable but adds infrastructure complexity and moves away from a pure Python stack
* **Cookie-based authentication** — explicitly not adopted due to YouTube's policy of permanently banning authenticated accounts used for scraping
* **Request counting with a daily cap** — replaced by the simpler and more robust approach of letting failures speak for themselves rather than managing a counter

The chosen architecture keeps the stack clean and Python-native, degrades gracefully rather than crashing, and is production-ready with a paid proxy plan.

---

## Current Limitations & Tradeoffs

* **In-memory storage** — vector stores and transcripts are scoped to the session, keeping the architecture lightweight and stateless; persistent storage (Redis, Pinecone) is a straightforward future addition
* **Transcript availability** — videos without captions gracefully fall back to a manual paste UI, so no video is ever a hard failure
* **In-memory processing** — keeps the stack simple and dependency-free for now, with a clear upgrade path to persistent vector databases
* **No authentication or rate limiting** — appropriate for a learning and portfolio project; production hardening is well-understood and documented in Future Improvements
* **Webshare free tier** — the proxy architecture is fully implemented and production-ready; reliable auto-fetch on cloud simply requires upgrading to a paid residential proxy plan

---

## Future Improvements

* Redis caching for transcript and vector store persistence across restarts
* Persistent vector database (Chroma / Pinecone)
* Paid Webshare residential proxy plan for reliable auto-fetch on cloud
* Multi-video querying
* Streaming responses
* Authentication and rate limiting
* CI/CD pipeline
* UI enhancements

---

## Tech Stack

### Backend

* FastAPI
* LangChain
* FAISS
* HuggingFace Inference API
* youtube-transcript-api v1.2.4
* Webshare residential proxies

### Frontend

* Streamlit

### Deployment

* Docker (backend)
* Render (backend hosting)
* Streamlit Community Cloud (frontend hosting)