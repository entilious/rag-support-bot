# test_demo.py
from bot import bot
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "demo-session-1"}}

print("Customer support bot ready. Type 'quit' to exit, 'reset' to start a new conversation.\n")

while True:
    try:
        q = input("🧑 You: ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if not q:
        continue
    if q.lower() == "quit":
        break
    if q.lower() == "reset":
        import uuid
        config = {"configurable": {"thread_id": f"demo-{uuid.uuid4()}"}}
        print("🔄 New conversation started.\n")
        continue

    out = bot.invoke({"messages": [HumanMessage(q)]}, config)

    print(f"   [category: {out.get('category', '?')}]", end="")
    if out.get("context"):
        topics = [line.split("---")[0].strip() for line in out["context"].split("\n\n")
                  if line.startswith("Support topic:")]
        print(f" [retrieved: {', '.join(t.replace('Support topic: ', '') for t in topics)}]")
    else:
        print()
    print(f"🤖 Bot: {out['messages'][-1].content}\n")