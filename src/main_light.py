"""
main_light.py — Lightweight FastAPI application for Render.com free tier (512MB RAM).

This version removes document processing (PDFs, images, embeddings) to fit within memory limits.
Keeps only: Free chat, Web search, URL summarization.

Routes:
    GET  /              → Render the main chat UI
    POST /chat          → Answer freely using LLM
    POST /chat/web      → Answer using real-time web search
    POST /chat/url      → Fetch and summarize a URL
    POST /reset         → Clear session state
    GET  /status        → Return current app state
    GET  /export/markdown → Download conversation as Markdown
"""

import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# ─── Load environment variables ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ─── LLM Client ───────────────────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def _make_client():
    """Create the LLM client."""
    if LLM_PROVIDER == "groq":
        from groq import Groq
        if not GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set in your .env file.")
        print(f"LLM provider: Groq  |  model: {GROQ_MODEL}")
        return Groq(api_key=GROQ_API_KEY)
    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Use: groq")

llm_client = _make_client()

# ─── App Initialization ───────────────────────────────────────────────────────

app = FastAPI(
    title="Nexus AI (Lightweight)",
    description="A lightweight AI assistant: chat freely, search the web, summarize URLs.",
    version="3.0.0-lite",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files & Templates ─────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ─── In-Memory Session State ──────────────────────────────────────────────────

class AppState:
    conversation: list = []
    mode: str = "free"

state = AppState()


# ─── Pydantic Request Models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str

class WebChatRequest(BaseModel):
    question: str

class UrlChatRequest(BaseModel):
    url: str
    question: str = ""


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", summary="Render the chat UI")
async def index(request: Request):
    """Serve the main chat interface page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "uploaded_files": [],
            "mode": state.mode,
        },
    )


@app.get("/status", summary="Get current app status")
async def status():
    """Return the current session state."""
    return JSONResponse({
        "mode": state.mode,
        "docs_indexed": False,
        "uploaded_files": [],
        "total_chunks": 0,
        "conversation_len": len(state.conversation),
    })


@app.post("/chat", summary="Chat with the AI (free mode)")
async def chat(req: ChatRequest):
    """Answer the user's question using LLM general knowledge."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = generate_free_answer(req.question, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user", "content": req.question})
    state.conversation.append({"role": "assistant", "content": result["answer"]})

    return JSONResponse({
        "answer": result["answer"],
        "sources": result["sources"],
        "mode": result.get("mode", state.mode),
    })


@app.post("/chat/web", summary="Answer using real-time web search")
async def chat_web(req: WebChatRequest):
    """Perform a DuckDuckGo search and generate a grounded answer."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    from src.services.web_search import search as web_search
    results = web_search(req.question, max_results=4)

    try:
        result = generate_web_answer(req.question, results, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user", "content": f"[Web search] {req.question}"})
    state.conversation.append({"role": "assistant", "content": result["answer"]})

    return JSONResponse({
        "answer": result["answer"],
        "sources": result["sources"],
        "mode": "web",
    })


@app.post("/chat/url", summary="Fetch and summarize a URL")
async def chat_url(req: UrlChatRequest):
    """Fetch a URL and summarize it using the LLM."""
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty.")

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    from src.services.web_search import fetch_url_content
    page_text = await fetch_url_content(url)

    if not page_text:
        raise HTTPException(
            status_code=422,
            detail=f"Could not fetch content from '{url}'."
        )

    question = req.question.strip() or f"Summarize this page: {url}"

    try:
        result = summarize_url_content(url, page_text, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user", "content": question})
    state.conversation.append({"role": "assistant", "content": result["answer"]})

    return JSONResponse({
        "answer": result["answer"],
        "sources": result["sources"],
        "mode": "url",
    })


@app.post("/reset", summary="Clear conversation memory")
async def reset():
    """Reset the application state."""
    state.conversation = []
    state.mode = "free"
    return JSONResponse({"status": "ok", "message": "Session reset successfully.", "mode": "free"})


@app.get("/export/markdown", summary="Export conversation as Markdown")
async def export_markdown():
    """Download the full conversation history as a formatted Markdown file."""
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No conversation to export yet.")

    lines = [
        "# Chat Export",
        f"\n_Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
        "---\n",
    ]

    for turn in state.conversation:
        role = turn["role"]
        content = turn["content"]
        if role == "user":
            lines.append(f"### 🧑 You\n\n{content}\n")
        else:
            lines.append(f"### 🤖 Assistant\n\n{content}\n")
        lines.append("---\n")

    md_content = "\n".join(lines)

    return Response(
        content=md_content.encode("utf-8"),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="chat-export-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md"'
        },
    )


# ─── LLM Functions ────────────────────────────────────────────────────────────

def generate_free_answer(user_question: str, conversation_history: list[dict]) -> dict:
    """Answer any question freely using the LLM's built-in knowledge."""
    system_prompt = (
        "You are Nexus AI, a sharp and concise AI assistant. "
        "Answer the user's question directly and accurately.\n\n"
        "Rules:\n"
        "- Use the conversation history above to answer follow-up questions.\n"
        "- Give well-structured answers using Markdown.\n"
        "- For code, always use fenced code blocks with the language name.\n"
        "- If you are unsure, say so — do not guess or invent facts.\n"
        "- Be concise when appropriate; be detailed when the question is complex."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history[-20:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_question})

    response = llm_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=3000,
    )

    return {"answer": response.choices[0].message.content.strip(), "sources": [], "mode": "free"}


def generate_web_answer(user_question: str, web_results: list[dict], conversation_history: list[dict]) -> dict:
    """Answer a question using real-time web search results as context."""
    if not web_results:
        result = generate_free_answer(user_question, conversation_history)
        result["mode"] = "web"
        return result

    context_parts = []
    for i, r in enumerate(web_results, 1):
        context_parts.append(
            f"[Web Result {i}] {r['title']}\n"
            f"URL: {r['url']}\n"
            f"{r['snippet']}"
        )
    context_text = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "You are Nexus AI. Answer the user's question using the web search results below.\n\n"
        "Rules:\n"
        "1. Answer directly and factually based on the search results.\n"
        "2. Mention the source title or URL inline when you use a specific result.\n"
        "3. Do NOT add a separate 'Sources' section — sources are shown automatically in the UI.\n"
        "4. If the results don't contain enough info, say so clearly instead of guessing.\n"
        "5. Keep the answer focused, structured, and free of filler.\n\n"
        f"WEB SEARCH RESULTS:\n{context_text}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    for turn in conversation_history[-10:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_question})

    response = llm_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=2000,
    )

    answer = response.choices[0].message.content.strip()
    sources = [{"title": r["title"], "url": r["url"]} for r in web_results]

    return {"answer": answer, "sources": sources, "mode": "web"}


def summarize_url_content(url: str, page_text: str, conversation_history: list[dict]) -> dict:
    """Summarize the content of a fetched URL."""
    system_prompt = (
        "You are Nexus AI. Provide a concise, structured summary of the web page content below.\n\n"
        "Rules:\n"
        "1. Extract only information present in the page text — do not add outside knowledge.\n"
        "2. Start with 1-2 sentences on what the page is about.\n"
        "3. Follow with a bullet list of key points and takeaways.\n"
        "4. If the content is unclear or sparse, state that briefly.\n"
        "5. Format using Markdown.\n\n"
        f"PAGE URL: {url}\n\nPAGE CONTENT:\n{page_text[:4000]}"
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.append({"role": "user", "content": "Summarize this page."})

    response = llm_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1500,
    )

    answer = response.choices[0].message.content.strip()
    return {"answer": answer, "sources": [{"title": url, "url": url}], "mode": "url"}


# ─── Dev Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main_light:app", host="0.0.0.0", port=8000, reload=True)
