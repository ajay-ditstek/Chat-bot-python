"""
main.py — FastAPI application entry point for the Universal AI Chatbot.

Routes:
    GET  /              → Render the main chat UI
    POST /upload/document → Upload any file (image, PDF, Word, text, etc.)
    POST /chat          → Answer freely or using document context (auto-detected)
    POST /chat/web      → Answer using real-time web search
    POST /chat/url      → Fetch and summarize a URL
    POST /reset         → Clear session state
    GET  /status        → Return current app state
    GET  /export/markdown → Download conversation as Markdown
"""

import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.rag_engine import (
    extract_text_from_pdfs,
    split_into_chunks,
    build_faiss_index,
    retrieve_context,
    generate_answer,
    generate_free_answer,
    generate_web_answer,
    analyze_image,
    analyze_document_with_context,
    summarize_url_content,
)
from src.services.web_search import search as web_search

# ─── App Initialization ───────────────────────────────────────────────────────

app = FastAPI(
    title="Universal AI Chatbot",
    description="A powerful AI assistant: chat freely, analyze any document, search the web, and more.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files & Templates ─────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# ─── Upload Directories ───────────────────────────────────────────────────────

UPLOAD_DIR   = BASE_DIR / "uploaded_pdfs"
IMAGE_DIR    = BASE_DIR / "uploaded_images"
DOCS_DIR     = BASE_DIR / "uploaded_docs"
UPLOAD_DIR.mkdir(exist_ok=True)
IMAGE_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

# ─── Supported file type categories ──────────────────────────────────────────

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"}
PDF_EXTENSIONS   = {".pdf"}
DOC_EXTENSIONS   = {".doc", ".docx", ".odt", ".txt", ".rtf", ".csv", ".md", ".html", ".htm", ".xml", ".json"}

# ─── In-Memory Session State ──────────────────────────────────────────────────

class AppState:
    faiss_index        = None
    chunks: list       = []
    uploaded_files: list[str] = []
    conversation: list = []       # [{role, content, mode?, timestamp?}, ...]
    mode: str          = "free"   # "free" | "document"

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
            "uploaded_files": state.uploaded_files,
            "mode": state.mode,
        },
    )


@app.get("/status", summary="Get current app status")
async def status():
    """Return the current session state."""
    return JSONResponse({
        "mode":            state.mode,
        "docs_indexed":    len(state.chunks) > 0,
        "uploaded_files":  state.uploaded_files,
        "total_chunks":    len(state.chunks),
        "conversation_len": len(state.conversation),
    })


# ─── Unified Document / Image Upload ─────────────────────────────────────────

@app.post("/upload/document", summary="Upload any file — image, PDF, Word doc, text, etc.")
async def upload_document(
    file: UploadFile = File(...),
    question: str = Form(default=""),
):
    """
    Accept ANY file upload:
    - Images  → Analyzed by vision model
    - PDFs    → Extracted, chunked, indexed into FAISS
    - Word/text/etc. → Text extracted and indexed into FAISS

    The user can provide their own question/description via the `question` field.
    If empty, a sensible default is used.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    ext = Path(file.filename).suffix.lower()
    file_bytes = await file.read()

    # ── Image: analyze via vision model ──────────────────────────────────────
    if ext in IMAGE_EXTENSIONS:
        prompt = question.strip() or "Please describe and analyze this file in detail."

        try:
            result = analyze_image(file_bytes, prompt, state.conversation)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Image analysis failed: {e}")

        state.conversation.append({"role": "user",      "content": f"[Image: {file.filename}] {prompt}"})
        state.conversation.append({"role": "assistant",  "content": result["answer"]})

        if file.filename not in state.uploaded_files:
            state.uploaded_files.append(file.filename)

        return JSONResponse({
            "answer":   result["answer"],
            "sources":  result["sources"],
            "mode":     "image",
            "filename": file.filename,
            "file_type": "image",
        })

    # ── PDF: extract, chunk, and index ────────────────────────────────────────
    elif ext in PDF_EXTENSIONS:
        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        save_path   = UPLOAD_DIR / unique_name

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        try:
            pages  = extract_text_from_pdfs([str(save_path)])
            chunks = split_into_chunks(pages)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {e}")

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No readable text found in the uploaded PDF. "
                       "If the PDF is scanned/image-based, OCR may be required."
            )

        all_chunks = state.chunks + chunks
        index, all_chunks = build_faiss_index(all_chunks)

        state.faiss_index = index
        state.chunks      = all_chunks
        state.mode        = "document"

        if file.filename not in state.uploaded_files:
            state.uploaded_files.append(file.filename)

        # Auto-answer the user's question if provided
        answer = None
        if question.strip():
            try:
                retrieved = retrieve_context(question, state.faiss_index, state.chunks)
                result    = generate_answer(question, retrieved, state.conversation)
                answer    = result["answer"]
                state.conversation.append({"role": "user",     "content": f"[Doc: {file.filename}] {question}"})
                state.conversation.append({"role": "assistant", "content": answer})
            except Exception:
                pass

        return JSONResponse({
            "answer":        answer or f"✅ **{file.filename}** uploaded and indexed successfully ({len(chunks)} chunks). You can now ask questions about it.",
            "sources":       [],
            "mode":          "document",
            "filename":      file.filename,
            "file_type":     "pdf",
            "total_chunks":  len(state.chunks),
        })

    # ── Other docs: extract text and index ────────────────────────────────────
    else:
        # Try to extract text generically
        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        save_path   = DOCS_DIR / unique_name

        with open(save_path, "wb") as f:
            f.write(file_bytes)

        try:
            result = analyze_document_with_context(
                file_bytes=file_bytes,
                filename=file.filename,
                ext=ext,
                question=question.strip() or "Please analyze and describe the contents of this document.",
                conversation_history=state.conversation,
                state=state,
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Document processing failed: {e}")

        if file.filename not in state.uploaded_files:
            state.uploaded_files.append(file.filename)

        state.conversation.append({"role": "user",     "content": f"[File: {file.filename}] {question or 'Analyze this document.'}"})
        state.conversation.append({"role": "assistant", "content": result["answer"]})

        return JSONResponse({
            "answer":    result["answer"],
            "sources":   result["sources"],
            "mode":      result["mode"],
            "filename":  file.filename,
            "file_type": "document",
        })


# ─── Legacy PDF upload route (kept for compatibility) ─────────────────────────

@app.post("/upload", summary="Legacy: Upload PDF files (use /upload/document instead)")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    """Legacy endpoint — delegates to the unified document handler."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    saved_paths = []
    filenames   = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"'{file.filename}' is not a PDF. Use /upload/document for all file types."
            )

        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        save_path   = UPLOAD_DIR / unique_name

        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        saved_paths.append(str(save_path))
        filenames.append(file.filename)

        if file.filename not in state.uploaded_files:
            state.uploaded_files.append(file.filename)

    try:
        pages  = extract_text_from_pdfs(saved_paths)
        chunks = split_into_chunks(pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {e}")

    if not chunks:
        raise HTTPException(status_code=422, detail="No readable text found in the uploaded PDF(s).")

    all_chunks = state.chunks + chunks
    index, all_chunks = build_faiss_index(all_chunks)

    state.faiss_index = index
    state.chunks      = all_chunks
    state.mode        = "document"

    return JSONResponse({
        "status":         "ok",
        "mode":           "document",
        "files_received": filenames,
        "total_chunks":   len(state.chunks),
        "message":        f"Successfully indexed {len(chunks)} new chunks from {len(files)} file(s).",
    })


# ─── Chat (Free + Document mode, auto-detected) ───────────────────────────────

@app.post("/chat", summary="Chat with the AI (free or document mode)")
async def chat(req: ChatRequest):
    """
    Answer the user's question.

    - If no document is indexed → Free chat using LLM general knowledge.
    - If documents are indexed  → Retrieve relevant chunks + document-augmented answer.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        if state.faiss_index is None or not state.chunks:
            # ── Free chat mode ─────────────────────────────────────────────
            result = generate_free_answer(req.question, state.conversation)
        else:
            # ── Document-augmented mode ────────────────────────────────────
            retrieved = retrieve_context(req.question, state.faiss_index, state.chunks)
            result    = generate_answer(req.question, retrieved, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user",      "content": req.question})
    state.conversation.append({"role": "assistant",  "content": result["answer"]})

    return JSONResponse({
        "answer":  result["answer"],
        "sources": result["sources"],
        "mode":    result.get("mode", state.mode),
    })


# ─── Web Search Chat ──────────────────────────────────────────────────────────

@app.post("/chat/web", summary="Answer using real-time web search")
async def chat_web(req: WebChatRequest):
    """
    Perform a DuckDuckGo search for the user's question, then use the
    search results as context to generate a grounded, cited answer.
    """
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Perform the search
    results = web_search(req.question, max_results=4)

    try:
        result = generate_web_answer(req.question, results, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user",      "content": f"[Web search] {req.question}"})
    state.conversation.append({"role": "assistant",  "content": result["answer"]})

    return JSONResponse({
        "answer":  result["answer"],
        "sources": result["sources"],
        "mode":    "web",
    })


# ─── URL Summarization ────────────────────────────────────────────────────────

@app.post("/chat/url", summary="Fetch and summarize a URL")
async def chat_url(req: UrlChatRequest):
    """
    Fetch a URL, extract its text content, and summarize it using the LLM.
    """
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
            detail=f"Could not fetch content from '{url}'. The page may be blocked or require JavaScript."
        )

    question = req.question.strip() or f"Summarize this page: {url}"

    try:
        result = summarize_url_content(url, page_text, state.conversation)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    state.conversation.append({"role": "user",      "content": question})
    state.conversation.append({"role": "assistant",  "content": result["answer"]})

    return JSONResponse({
        "answer":  result["answer"],
        "sources": result["sources"],
        "mode":    "url",
    })


# ─── Reset ────────────────────────────────────────────────────────────────────

@app.post("/reset", summary="Clear conversation memory and uploaded documents")
async def reset():
    """
    Reset the application state: wipe the FAISS index, chunk list,
    conversation history, and delete all saved files.
    """
    state.faiss_index     = None
    state.chunks          = []
    state.uploaded_files  = []
    state.conversation    = []
    state.mode            = "free"

    for directory in [UPLOAD_DIR, IMAGE_DIR, DOCS_DIR]:
        for f in directory.iterdir():
            if f.is_file():
                f.unlink()

    return JSONResponse({"status": "ok", "message": "Session reset successfully.", "mode": "free"})


# ─── Export Conversation ──────────────────────────────────────────────────────

@app.get("/export/markdown", summary="Export conversation as Markdown")
async def export_markdown():
    """
    Download the full conversation history as a formatted Markdown file.
    """
    if not state.conversation:
        raise HTTPException(status_code=400, detail="No conversation to export yet.")

    lines = [
        "# Chat Export",
        f"\n_Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n",
    ]

    if state.uploaded_files:
        lines.append("**Documents:** " + ", ".join(state.uploaded_files) + "\n")

    lines.append("---\n")

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


# ─── Dev Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
