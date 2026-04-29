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

### Option 1: Replit (Recommended - Easiest, Free with Good Resources)

Replit is the easiest platform for deploying Python apps with minimal setup.

**Features:**
- ✅ Free chat with LLM
- ✅ Web search
- ✅ URL summarization
- ✅ PDF/image upload and document analysis
- ✅ Up to 500MB-1GB RAM on free tier
- ✅ One-click deployment
- ✅ Built-in IDE and terminal
- ✅ No SSH or configuration needed

**Prerequisites:**
- Replit account (free)
- GROQ_API_KEY from https://console.groq.com

**Step-by-Step Deployment:**

1. **Create a Replit:**
   - Go to https://replit.com
   - Click "Create Repl"
   - Template: "Python" or "Blank Repl"
   - Name: `nexus-ai`

2. **Import Your Code:**
   - Option A: Click "Import from GitHub" and paste your repo URL
   - Option B: Copy all files from your local project to Replit

3. **Install Dependencies:**
   - Open the Shell tab in Replit
   - Run: `pip install -r requirements.txt`

4. **Set Environment Variables:**
   - Click the "Secrets" (lock icon) in the left sidebar
   - Add:
     - `GROQ_API_KEY`: Your Groq API key
     - `LLM_PROVIDER`: `groq`
     - `GROQ_MODEL`: `llama-3.3-70b-versatile`

5. **Run the Application:**
   - In the Shell tab, run:
     ```bash
     uvicorn src.main:app --host 0.0.0.0 --port 8000
     ```

6. **Access Your App:**
   - Replit will show a "Webview" window with your app
   - Or click the "Open in Browser" button

**Important Notes:**
- **Always Running**: Free tier Repls sleep after inactivity (wakes on request)
- **Resource Limits**: Free tier has 500MB-1GB RAM
- **Easy to Use**: No SSH, no firewall configuration, just click and run

### Option 2: Koyeb (Git-based, Free Tier with 512MB RAM)

Koyeb offers Git-based deployment with Docker support and a free tier.

**Features:**
- ✅ Free chat with LLM
- ✅ Web search
- ✅ URL summarization
- ⚠️ PDF/image upload may have memory issues (512MB limit)
- ✅ Git-based deployment (auto-deploy on push)
- ✅ Custom domains on paid plans

**Prerequisites:**
- Koyeb account (free)
- GitHub repository with your code
- GROQ_API_KEY from https://console.groq.com

**Step-by-Step Deployment:**

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for Koyeb deployment"
   git push origin main
   ```

2. **Sign up at Koyeb:**
   - Go to https://www.koyeb.com
   - Create a free account

3. **Create a new App:**
   - Click "Create App"
   - Select "GitHub" as the source
   - Connect your GitHub account
   - Select your repository

4. **Configure Build:**
   - Builder: Choose "Buildpacks" (auto-detects Python)
   - OR choose "Docker" if you have a Dockerfile
   - Python version: 3.10 or 3.11

5. **Set Environment Variables:**
   - Go to your app settings
   - Add environment variables:
     - `GROQ_API_KEY`: Your Groq API key
     - `LLM_PROVIDER`: `groq`
     - `GROQ_MODEL`: `llama-3.3-70b-versatile`

6. **Configure Port:**
   - In app settings, set the port to `8000`
   - Koyeb will automatically detect and expose this port

7. **Deploy:**
   - Click "Deploy"
   - Koyeb will build and deploy your app

8. **Access Your App:**
   - Koyeb will provide a URL like `https://your-app.koyeb.app`

**Important Notes:**
- **Sleep Mode**: Free tier apps sleep after inactivity (wakes on request)
- **Memory Limit**: Free tier has 512MB RAM - may encounter out-of-memory errors with full version
- **Use lightweight version**: If you get memory errors, use `requirements-light.txt` and `src/main_light.py`
- **Auto-deploy**: Pushing to GitHub automatically redeploys

### Option 3: Oracle Cloud Free Tier (Advanced - Up to 24GB RAM)

Oracle Cloud offers the most resources but requires technical knowledge.

**Features:**
- ✅ Full features with document processing
- ✅ Up to 24GB RAM
- ✅ 200GB storage
- ✅ Always running (no sleep mode)

**Requirements:**
- SSH knowledge
- Linux command line experience
- Credit card for verification (no charges)

**See README for detailed Oracle Cloud instructions.**

### Option 3: Streamlit Cloud (Free with 1GB RAM - Lightweight Only)

Streamlit Cloud is easy but only supports the lightweight version.

**Features:**
- ✅ Free chat, web search, URL summarization
- ❌ No PDF/image upload (memory limited)
- ✅ Easy GitHub integration

**See README for detailed Streamlit Cloud instructions.**

### Why Not Netlify?

**Netlify does NOT support Python web applications.**

Netlify is designed for:
- Static HTML/CSS/JavaScript sites
- Serverless functions (JavaScript/TypeScript)
- JAMstack applications

**Netlify cannot run:**
- FastAPI applications
- Streamlit applications
- Python web servers
- Applications with dependencies like sentence-transformers, FAISS, etc.

**For Python apps, use:**
- **Replit** (easiest, recommended)
- **Oracle Cloud** (most resources, advanced)
- **Streamlit Cloud** (easy, lightweight only)

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
