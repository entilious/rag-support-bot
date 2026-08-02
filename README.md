# Customer Support Chatbot (RAG + LangGraph)

My first hands-on project exploring **RAG** (Retrieval-Augmented Generation)
and **LangGraph**. I built a simple customer support chatbot that answers
questions using a knowledge base instead of making things up.

This project was mainly a learning exercise. I wanted to understand how
real support bots work under the hood, so I built one from scratch and
packaged it with Docker.

## Demo

Watch the bot in action:

<!-- TODO: drag and drop the demo video here while editing this file on GitHub -->

## What it does

- Answers customer support questions (orders, refunds, delivery, payments, etc.)
- Looks up answers from a knowledge base using vector search (RAG)
- Remembers the conversation, so follow-up questions work
- Detects the topic of each question to narrow down the search
- Knows when to say "let me connect you to a human" instead of guessing
- Has a web UI (Streamlit) and an API backend (FastAPI)

## How it works

1. A question comes in through the Streamlit UI
2. FastAPI passes it to a LangGraph agent
3. The agent classifies the topic (order? refund? delivery?)
4. It searches the knowledge base (Chroma vector store) for matching answers
5. The LLM (Perplexity Sonar) writes a friendly reply using what was found

The knowledge base is built from the **Bitext customer support dataset**
(27K real support Q&A pairs), indexed at startup by `ingest_demo.py`.

## Tech stack

| Piece | What I used |
|---|---|
| Agent framework | LangGraph |
| LLM | Perplexity Sonar |
| Embeddings | sentence-transformers (local, free) |
| Vector store | Chroma |
| Backend | FastAPI |
| Frontend | Streamlit |
| Packaging | Docker Compose |

## Project structure

```
├── kbase.py       # builds the knowledge base
├── bot.py         # the LangGraph agent
├── api.py         # FastAPI backend
├── app.py         # Streamlit frontend

```

## Run it

```bash
# 1. Add your Perplexity API key
conda create -m [env-name] python
export PPLX_API_KEY='pplx-your-key-here'

# 2. Start everything: run the following commands on two different terminal windows
uvicorn api:app --reload --port 8000
streamlit run app.py --server.headless true

# 3. Open the UI
# http://localhost:8501
```

The API docs are at http://localhost:8000/docs if you want to poke at the
backend directly.

## What I learned

- How a RAG pipeline actually flows: retrieve, grade, generate
- LangGraph state graphs, conditional routing, and memory (checkpointers)
- Why filtering retrieval by metadata matters for answer quality
- Wiring an AI backend into a real UI and packaging it all in Docker

## If I build on this

- Stream responses token-by-token
- Add tools so the bot can look up real orders, not just answer questions
- Swap in-memory chat history for a database so sessions survive restarts
