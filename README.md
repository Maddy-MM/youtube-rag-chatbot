# YTLens

A **Retrieval-Augmented Generation (RAG) system** that allows users to ask questions about any YouTube video using its transcript. The system retrieves relevant context and generates grounded responses using a Large Language Model.

---

## Table of Contents

1. Overview
2. Features
3. Project Workflow
4. RAG Pipeline Architecture
5. Authentication
6. API Endpoints
7. Frontend
8. Project Structure
9. Installation & Setup
10. How to Run
11. Deployment Architecture
12. Transcript Fetching Strategy
13. Current Limitations & Tradeoffs
14. Future Improvements
15. Tech Stack

---

## Overview

This project implements an **end-to-end GenAI pipeline** with a modular architecture:

- **FastAPI backend** handles the RAG pipeline and authentication
- **Streamlit frontend** provides a JWT-authenticated chat interface
- Components are independently deployable

The system ensures responses remain **grounded in transcript data** to reduce hallucinations.

---

## Live Demo

- **Backend API:** [YTLens - Backend (Render)](https://youtube-rag-backend-js1w.onrender.com/)
- **Frontend:** [YTLens - Frontend (Streamlit)](https://youtube-rag-chatbot-jixvzdtnxgbinlnnr4hbqo.streamlit.app/)

> **Note:** The backend is hosted on Render's free tier and may take 30–60 seconds to wake up on the first request.

**Demo credentials:**

- Username: `admin`
- Password: `admin123`

---

## Features

- JWT-authenticated access — login required before using the app
- Ask questions about any YouTube video
- Two-layer transcript fetching with graceful degradation
- Residential proxy support via Webshare for cloud IP bypass — skipped automatically if credentials are not configured, adding zero latency
- Manual transcript paste fallback when auto-fetch fails
- Context-aware responses using MMR retrieval and BGE embeddings
- Semantic search using FAISS
- LLM-based answer generation via HuggingFace Inference API
- Streamlit chat interface with custom dark theme and YTLens branding
- Modular API-based backend
- Docker support for deployment
- UptimeRobot health monitoring to prevent cold starts on Render free tier

---

## Project Workflow

1. User logs in with username and password
2. JWT token issued and stored for the session
3. User provides a YouTube video URL
4. Extract video ID
5. Attempt transcript fetch — direct, then proxy (if credentials configured), then manual paste
6. Split transcript into chunks
7. Generate embeddings
8. Store embeddings in vector database
9. Retrieve relevant chunks based on user question using MMR
10. Pass context + query to LLM
11. Return generated response

---

## RAG Pipeline Architecture

### Transcript Extraction

- Uses `youtube-transcript-api` v1.2.4
- Two-layer fetching strategy (see Transcript Fetching Strategy section)
- Attempts English transcript first, falls back to any available language

### Text Splitting

- `RecursiveCharacterTextSplitter` tuned for transcript content
- Chunk size: 600
- Overlap: 150
- Custom separators prioritise sentence boundaries (`". "`, `"? "`, `"! "`) before falling back to word boundaries — minimises mid-sentence cuts common in transcript text

### Embeddings

- Model: `BAAI/bge-small-en-v1.5`
- Upgraded from the tutorial-standard `all-MiniLM-L6-v2` — BGE consistently outperforms MiniLM on standard retrieval benchmarks (MTEB, BEIR) while remaining small enough to run on CPU
- `normalize_embeddings=True` required for correct cosine similarity scoring

### Vector Store

- FAISS for fast in-memory similarity search
- In-memory caching via `vector_store_cache` dictionary

### Retrieval

- **MMR (Maximal Marginal Relevance)** instead of plain similarity search
- Plain similarity search frequently returns redundant chunks from the same segment — MMR balances relevance with diversity, giving the LLM broader context from across the video
- `k=5`, `fetch_k=20`, `lambda_mult=0.7` — leans towards relevance while still enforcing chunk diversity

### LLM

- Model: `openai/gpt-oss-20b` (via HuggingFace Inference API)
- Temperature: 0.2
- Structured prompt with numbered excerpts (`[Excerpt 1]`, `[Excerpt 2]`...) and explicit instructions for sufficient, partial, and insufficient context cases
- `ANSWER:` suffix helps open source models identify where to begin generating

---

## Authentication

YTLens uses **JWT-based authentication**. A login is required before accessing any part of the application.

- Passwords are hashed with **bcrypt** — no plaintext passwords are stored
- On login, the backend issues a signed JWT token valid for 8 hours
- All protected endpoints verify the token via a FastAPI `HTTPBearer` dependency
- User data is persisted in **SQLite via SQLAlchemy**
- A default admin user is seeded from environment variables on every backend startup

> **Note on Render's free tier:** Render has an ephemeral filesystem — the SQLite database is wiped on every redeploy. The default admin user is re-seeded automatically on startup so the app is always accessible. Registered users added at runtime will not survive a redeploy. Migrating to a persistent database (Neon, Supabase) is a straightforward connection string change.

**Public endpoints:** `/health`, `/login`

**Protected endpoints:** `/process_video`, `/process_video_manual`, `/ask`

---

## API Endpoints

### Health Check

`GET /health` — Returns `{"status": "ok"}` instantly with no ML or DB calls. Used by UptimeRobot to ping the backend every 5 minutes to keep the Render free tier container warm.

### Login

`POST /login` — Accepts `username` and `password`. Returns a signed JWT `access_token` on success, HTTP 401 on invalid credentials.

### Process Video

`POST /process_video` _(protected)_ — Attempts to fetch transcript automatically and builds the vector store. Returns `{"error": "fallback"}` if both fetch layers fail, signalling the frontend to show the manual paste UI.

### Process Video Manual

`POST /process_video_manual` _(protected)_ — Accepts a manually pasted transcript and runs it through the same pipeline as an auto-fetched transcript — split, embed, store. The `/ask` endpoint works identically regardless of how the transcript arrived.

### Ask Question

`POST /ask` _(protected)_ — Returns context-aware answers based on transcript chunks retrieved via MMR.

---

## Frontend

Built with Streamlit:

- Login screen with JWT authentication — distinct centered layout, separate from the rest of the app
- Video URL input with "Analyse Video" action
- Processing feedback with spinner
- Automatic transcript fetch with proxy fallback
- Manual transcript paste UI when auto-fetch fails, directing users to [youtubetotranscript.com](https://youtubetotranscript.com/)
- Video thumbnail and title preview via YouTube oEmbed API
- Chat interface with message history
- Logout button in sidebar

### User Flow

1. Sign in with username and password
2. Paste video link and click Analyse Video
3. Preview video thumbnail and title
4. Start chatting

---

## Project Structure

```text
youtube-rag-assistant/
│
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── main.py
│   │
│   ├── src/
│   │   ├── auth.py
│   │   ├── database.py
│   │   │
│   │   └── rag/
│   │       ├── __init__.py
│   │       ├── ingest.py
│   │       ├── splitter.py
│   │       ├── embeddings.py
│   │       ├── retriever.py
│   │       └── chains.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   └── .env
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   │
│   └── .streamlit/
│       └── config.toml
│
├── .gitignore
└── README.md
```

---

## Installation & Setup

### Clone Repository

```bash
git clone https://github.com/<your-username>/ytlens.git
cd ytlens
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

WEBSHARE_USER=your_webshare_username
WEBSHARE_PASS=your_webshare_password

JWT_SECRET=your_long_random_secret_string
DEFAULT_USER=admin
DEFAULT_PASS=admin123
```

> `WEBSHARE_USER` and `WEBSHARE_PASS` are optional — if not set the proxy layer is skipped entirely with zero added latency.

> `JWT_SECRET` falls back to a hardcoded dev string if not set — always set it properly in production.

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

> The frontend `API_URL` can be set as an environment variable to switch between local and deployed backend without code changes:
> 
> ```ini
> API_URL=http://127.0.0.1:8000  # local
> API_URL=https://youtube-rag-backend-js1w.onrender.com  # production
> ```

---

## Deployment Architecture

- Backend deployed as a Dockerized FastAPI service on Render
- Frontend deployed separately on Streamlit Community Cloud
- Communication via REST APIs with JWT Bearer token authentication
- Environment variables managed via Render dashboard and Streamlit secrets
- UptimeRobot monitors `/health` every 5 minutes to keep the backend warm on Render's free tier

---

## Transcript Fetching Strategy

YouTube blocks transcript fetch requests from cloud server IPs (Render, Streamlit Cloud, AWS, GCP etc.) because they originate from well-known datacenter IP ranges. This required building a robust two-layer fetching strategy with graceful degradation.

### Layer 1 — Direct Fetch

The system first attempts a direct fetch using `youtube-transcript-api` with no proxy. This works reliably in local environments and occasionally succeeds on cloud too depending on YouTube's current blocklist state. Tries English first, falls back to any available language.

### Layer 2 — Residential Proxy via Webshare

If the direct fetch fails and Webshare credentials are configured, the system retries using a Webshare residential proxy via the v1.2.4 `WebshareProxyConfig` API passed into the `YouTubeTranscriptApi` constructor. A hard 3-second timeout is enforced using `ThreadPoolExecutor` at the OS thread level — this kills the proxy attempt after exactly 3 seconds regardless of what the library does internally, including its own retry logic. `HTTPAdapter(max_retries=0)` is also set to prevent HTTP-level retries.

If credentials are not set, this layer is skipped instantly with no latency — making it safe to deploy without a paid proxy plan while keeping the full architecture intact for when credentials are added.

> **Note on the free tier:** Webshare's free tier provides shared datacenter proxies, not true residential proxies. These get blocked by YouTube just like regular cloud IPs. A paid Webshare residential proxy plan makes this layer fully reliable.

### Layer 3 — Manual Transcript Paste

If both fetch attempts fail, the backend returns `{"error": "fallback"}` and the frontend shows a manual paste UI directing the user to [youtubetotranscript.com](https://youtubetotranscript.com/). The pasted transcript is submitted to `/process_video_manual` and passed through the identical pipeline — split, embed, store — so the chat experience is unchanged.

---

## Current Limitations & Tradeoffs

- **In-memory vector storage** — vector stores are scoped to the server process; a server restart clears all cached video data. Redis or Pinecone would be a straightforward upgrade
- **Ephemeral user storage on Render free tier** — SQLite is wiped on every redeploy; the default admin is re-seeded automatically. Migrating to Neon or Supabase PostgreSQL is a one-line connection string change
- **Transcript availability** — videos without captions fall back gracefully to the manual paste UI; no video is ever a hard failure
- **Webshare free tier** — the proxy architecture is fully implemented; reliable auto-fetch on cloud requires upgrading to a paid residential proxy plan

---

## Future Improvements

- Persistent vector database (Chroma / Pinecone) for cross-session video caching
- Paid Webshare residential proxy plan for reliable auto-fetch on cloud
- Persistent database (Neon / Supabase) for stable multi-user support
- Streaming LLM responses
- Multi-video querying
- CI/CD pipeline

---

## Tech Stack

### Backend

- FastAPI
- LangChain
- FAISS
- HuggingFace Inference API (`BAAI/bge-small-en-v1.5` embeddings, `openai/gpt-oss-20b` LLM)
- youtube-transcript-api v1.2.4
- SQLite + SQLAlchemy
- JWT authentication (python-jose, passlib, bcrypt)
- Webshare residential proxies

### Frontend

- Streamlit
- Custom dark theme via `.streamlit/config.toml` — YouTube red accent, deep navy backgrounds, consistent typography

### Deployment

- Docker (backend)
- Render (backend hosting)
- Streamlit Community Cloud (frontend hosting)
- UptimeRobot (health monitoring)