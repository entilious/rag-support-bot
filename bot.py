from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_perplexity import ChatPerplexity              # was ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage

CATEGORIES = ["ACCOUNT","CANCELLATION_FEE","CONTACT","DELIVERY","FEEDBACK",
              "INVOICE","NEWSLETTER","ORDER","PAYMENT","REFUND",
              "SHIPPING_ADDRESS","GENERAL"]

llm = ChatPerplexity(model="sonar", temperature=0)   # reads PPLX_API_KEY [web:42]
vs = Chroma(persist_directory="./chroma_db",
            embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))

class State(TypedDict):
    messages: Annotated[list, add_messages]
    category: str
    context: str

def classify(state: State):
    q = state["messages"][-1].content
    out = llm.invoke([
        SystemMessage("Classify the user message into EXACTLY one word from: "
                      + ", ".join(CATEGORIES) + ". Reply with the word only."),
        HumanMessage(q)])
    cat = out.content.strip().upper().split()[0]
    return {"category": cat if cat in CATEGORIES else "GENERAL"}

def retrieve(state: State):
    retriever = vs.as_retriever(search_kwargs={
        "k": 3, "filter": {"category": state["category"]}})
    docs = retriever.invoke(state["messages"][-1].content)
    return {"context": "\n\n---\n\n".join(d.page_content for d in docs)}

GROUND_RULES = ("You are a friendly customer support agent. Do NOT use web search or "
                "outside knowledge. Answer ONLY from the context below. "
                "If it doesn't help, offer to connect a human agent.\n\n")

def generate(state: State):
    return {"messages": [llm.invoke(
        [SystemMessage(GROUND_RULES + state["context"])] + state["messages"])]}

def casual(state: State):
    return {"messages": [llm.invoke([SystemMessage(
        "You are a friendly customer support agent. Keep it brief and offer help.")
        ] + state["messages"])]}

g = StateGraph(State)
for n, f in [("classify", classify), ("retrieve", retrieve),
             ("generate", generate), ("casual", casual)]:
    g.add_node(n, f)
g.set_entry_point("classify")
g.add_conditional_edges("classify",
    lambda s: "casual" if s["category"] == "GENERAL" else "retrieve",
    {"casual": "casual", "retrieve": "retrieve"})
g.add_edge("retrieve", "generate")
g.add_edge("generate", END); g.add_edge("casual", END)

bot = g.compile(checkpointer=MemorySaver())