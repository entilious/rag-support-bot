import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from bot import bot   # your compiled graph

app = FastAPI(title="Customer Support Bot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "default"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    out = bot.invoke({"messages": [HumanMessage(req.query)]},
                     config={"configurable": {"thread_id": req.thread_id}})
    return {
        "response": out["messages"][-1].content,
        "category": out.get("category"),
    }