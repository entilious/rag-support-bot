import pandas as pd
from datasets import load_dataset
from collections import defaultdict
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings   # free, local
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

ds = load_dataset("bitext/Bitext-customer-support-llm-chatbot-training-dataset", split="train")
df = ds.to_pandas()

groups = defaultdict(list)
for _, r in df.sample(n=2000, random_state=42).iterrows():
    groups[(r["category"], r["intent"])].append(r)

docs = []
for (cat, intent), rows in groups.items():
    qa = "\n".join(f"Q: {x['instruction']}\nA: {x['response']}" for x in rows[:5])
    docs.append(Document(
        page_content=f"Support topic: {intent.replace('_', ' ')}\n\n{qa}",
        metadata={"category": cat, "intent": intent},
    ))

print(f"Indexed {len(docs)} intent documents")
Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")