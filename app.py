from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import ask_agent, create_conversation_history


app = FastAPI(
    title="AI Travel Planning Assistant"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversation_sessions = {}


@app.get("/")
def health_check():
    return {
        "message": "AI Travel Planning Assistant API is running"
    }


@app.post("/api/chat")
def chat(request: dict):

    question = request.get("question", "")
    session_id = request.get("session_id", "")

    if not question.strip():
        return {
            "answer": "Please enter a question.",
            "tools_used": [],
            "sources": [],
            "mcp_used": False
        }

    if not session_id:
        return {
            "answer": "Session ID is required.",
            "tools_used": [],
            "sources": [],
            "mcp_used": False
        }

    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = (
            create_conversation_history()
        )

    conversation_history = conversation_sessions[session_id]

    result = ask_agent(
        question,
        conversation_history
    )

    return result