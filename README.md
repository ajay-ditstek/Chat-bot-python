# Nexus AI - Universal AI Chatbot

A powerful AI assistant that can chat freely, analyze documents, search the web, and analyze images.

## Features

- **Free Chat** - General AI conversation using LLM knowledge
- **Document Analysis** - Upload PDFs, Word docs, text files, CSVs, HTML, JSON, etc.
- **Image Analysis** - Upload images for vision model analysis
- **Web Search** - Real-time DuckDuckGo search with LLM-grounded answers
- **URL Summarization** - Fetch and summarize web pages
- **Conversation Export** - Download chat history as Markdown

## Tech Stack

- **Backend**: FastAPI (Python)
- **LLM**: Groq (free), xAI, or OpenAI
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **PDF Processing**: PyMuPDF + Tesseract OCR
- **Web Search**: DuckDuckGo

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. **Run the application:**
   ```bash
   # Using the run script
   bash run.sh

   # Or directly with uvicorn
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

## Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free with 1GB RAM)

Streamlit Cloud offers a free tier with 1GB RAM, which is sufficient for this app.

**Features:**
- ✅ Free chat with LLM
- ✅ Web search
- ✅ URL summarization
- ✅ 1GB RAM (vs 512MB on Render)
- ✅ Easy deployment (just connect GitHub)

**Prerequisites:**
- Streamlit Cloud account (free)
- Git repository (GitHub)
- GROQ_API_KEY from https://console.groq.com

**Step-by-Step Deployment:**

1. **Push code to Git:**
   ```bash
   git add .
   git commit -m "Ready for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Sign up at Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Create a free account using GitHub

3. **Deploy your app:**
   - Click "New app"
   - Select your GitHub repository
   - Select the branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

4. **Set Environment Variables:**
   - Go to your app settings in Streamlit Cloud
   - Add secrets:
     - `GROQ_API_KEY`: Your Groq API key
     - `LLM_PROVIDER`: `groq`
     - `GROQ_MODEL`: `llama-3.3-70b-versatile`

5. **Access your app:**
   - Streamlit will provide a URL like `https://your-app.streamlit.app`
   - Visit the URL to test your application

**Important Notes:**
- **Sleep Mode**: Free tier apps sleep after inactivity (wakes on first request)
- **Resource Limits**: Free tier has 1GB RAM
- **Custom Domain**: Available on paid plans only

### Option 2: Render.com (Not Recommended - Only 512MB RAM)

Render.com's free tier has only 512MB RAM, which is insufficient for this app even in lightweight mode.

**If you still want to use Render.com:**
- You must use the lightweight version (`requirements-light.txt`, `src/main_light.py`)
- Even then, you may encounter out-of-memory errors
- Consider upgrading to Render's paid tier ($7/month for 1GB RAM)

### Option 3: Full Version (Document Processing)

For the full version with PDF/image upload and document analysis, you need:
- **Streamlit Cloud** (1GB RAM free tier) - Recommended
- **Render.com paid tier** ($7/month for 1GB RAM)
- **Railway.app** ($5 free credit, then paid)
- **PythonAnywhere** (free tier, but limited)

The full version requires:
- `requirements.txt` (includes embeddings, FAISS, PDF processing)
- `src/main.py` (full FastAPI app with document processing)

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `GROQ_API_KEY` - Your Groq API key (required)
- `LLM_PROVIDER` - LLM provider: `groq`, `xai`, or `openai` (default: groq)
- `GROQ_MODEL` - Groq model name (default: llama-3.3-70b-versatile)
- `GROQ_VISION_MODEL` - Vision model for image analysis
- `XAI_API_KEY` - xAI API key (if using xAI)
- `XAI_MODEL` - xAI model name
- `OPENAI_API_KEY` - OpenAI API key (if using OpenAI)
- `OPENAI_MODEL` - OpenAI model name

## License

MIT License
