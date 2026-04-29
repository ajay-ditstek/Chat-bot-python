"""
app.py — Streamlit version of Nexus AI for Streamlit Cloud deployment.

This version uses Streamlit for the UI, which is lighter and better suited for
free cloud deployment with higher memory limits.

Features:
- Free chat with LLM
- Web search
- URL summarization
"""

import os
from pathlib import Path
from dotenv import load_dotenv

import streamlit as st

# ─── Load environment variables ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
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
        return Groq(api_key=GROQ_API_KEY)
    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER '{LLM_PROVIDER}'. Use: groq")


llm_client = _make_client()


# ─── Web Search ───────────────────────────────────────────────────────────────
def web_search(query: str, max_results: int = 4) -> list[dict]:
    """Perform a DuckDuckGo search."""
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                )
        return results
    except Exception as e:
        st.error(f"Web search failed: {e}")
        return []


def fetch_url_content(url: str, max_chars: int = 4000) -> str:
    """Fetch and extract plain text from a URL."""
    import re
    import httpx

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        text = re.sub(
            r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(
            r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE
        )
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return text[:max_chars]
    except Exception as e:
        st.error(f"URL fetch failed: {e}")
        return ""


# ─── LLM Functions ────────────────────────────────────────────────────────────
def generate_free_answer(user_question: str, conversation_history: list[dict]) -> str:
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

    return response.choices[0].message.content.strip()


def generate_web_answer(
    user_question: str, web_results: list[dict], conversation_history: list[dict]
) -> str:
    """Answer a question using real-time web search results as context."""
    if not web_results:
        return generate_free_answer(user_question, conversation_history)

    context_parts = []
    for i, r in enumerate(web_results, 1):
        context_parts.append(
            f"[Web Result {i}] {r['title']}\n" f"URL: {r['url']}\n" f"{r['snippet']}"
        )
    context_text = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "You are Nexus AI. Answer the user's question using the web search results below.\n\n"
        "Rules:\n"
        "1. Answer directly and factually based on the search results.\n"
        "2. Mention the source title or URL inline when you use a specific result.\n"
        "3. If the results don't contain enough info, say so clearly instead of guessing.\n"
        "4. Keep the answer focused, structured, and free of filler.\n\n"
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

    return response.choices[0].message.content.strip()


def summarize_url_content(url: str, page_text: str) -> str:
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

    return response.choices[0].message.content.strip()


# ─── Streamlit UI ───────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Nexus AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ Nexus AI")
st.markdown("Your AI assistant for free chat, web search, and URL summarization.")

# Sidebar
with st.sidebar:
    st.header("Mode")
    mode = st.radio("Select Mode", ["Free Chat", "Web Search", "URL Summarize"])

    st.header("Conversation")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response based on mode
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if mode == "Free Chat":
                response = generate_free_answer(prompt, st.session_state.messages)
            elif mode == "Web Search":
                with st.spinner("Searching the web..."):
                    results = web_search(prompt)
                if results:
                    response = generate_web_answer(
                        prompt, results, st.session_state.messages
                    )
                    st.markdown("**Sources:**")
                    for r in results:
                        st.markdown(f"- [{r['title']}]({r['url']})")
                else:
                    response = "No search results found. Try a different query."
            elif mode == "URL Summarize":
                url = prompt.strip()
                if not (url.startswith("http://") or url.startswith("https://")):
                    url = "https://" + url
                with st.spinner("Fetching URL..."):
                    page_text = fetch_url_content(url)
                if page_text:
                    response = summarize_url_content(url, page_text)
                else:
                    response = "Could not fetch content from the URL. It may be blocked or require JavaScript."

        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
