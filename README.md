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

## Deployment to PythonAnywhere

### Prerequisites
- PythonAnywhere account (free tier)
- Git repository (GitHub, GitLab, or Bitbucket)
- GROQ_API_KEY from https://console.groq.com

### Step-by-Step Deployment

1. **Push code to Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-git-repo-url>
   git push -u origin main
   ```

2. **Sign up at PythonAnywhere:**
   - Go to https://www.pythonanywhere.com
   - Create a free account

3. **Create a new Web App:**
   - Go to the "Web" tab
   - Click "Add a new web app"
   - Choose "Manual Configuration"
   - Select Python 3.10 or higher
   - Click Next

4. **Configure the Web App:**
   - **WSGI configuration file**: Set path to `/var/www/<your-username>_pythonanywhere_com_wsgi.py`
   - **Working directory**: Set to your project folder
   - **Virtualenv**: Create a new virtualenv (Python 3.10+)

5. **Upload your code:**
   - Go to the "Files" tab
   - Navigate to your project folder
   - Use "Upload a file" or clone from git:
     ```bash
     git clone <your-git-repo-url>
     ```

6. **Install dependencies:**
   - Go to the "Consoles" tab
   - Start a Bash console
   - Navigate to your project folder
   - Activate virtualenv:
     ```bash
     source ~/virtualenvs/<your-webapp-name>/bin/activate
     ```
   - Install requirements:
     ```bash
     pip install -r requirements.txt
     ```

7. **Configure WSGI:**
   - Go to the "Web" tab
   - Click on the "WSGI configuration file" link
   - Replace the content with:
     ```python
     import os
     import sys
     from pathlib import Path

     # Add project to path
     project_home = '/home/<your-username>/<your-project-folder>'
     if project_home not in sys.path:
         sys.path = [project_home] + sys.path

     os.environ.setdefault('PYTHONPATH', project_home)

     from src.main import app
     application = app
     ```
   - Save and close

8. **Set Environment Variables:**
   - Go to the "Web" tab
   - Scroll to "Environment variables"
   - Add:
     - `GROQ_API_KEY`: Your Groq API key
     - `LLM_PROVIDER`: `groq`
     - `GROQ_MODEL`: `llama-3.3-70b-versatile`

9. **Configure Static Files:**
   - Go to the "Web" tab
   - Scroll to "Static files"
   - Add:
     - URL: `/static/`
     - Directory: `/home/<your-username>/<your-project-folder>/static`

10. **Reload the Web App:**
    - Click the "Reload" button in the Web tab
    - Wait for the app to restart

11. **Test the deployment:**
    - Visit `https://<your-username>.pythonanywhere.com`
    - Test the chat functionality

### Important Notes

- **Ephemeral Storage**: Uploaded files are lost when the app redeploys or restarts
- **Sleep Mode**: Free tier apps sleep after inactivity (wakes on first request)
- **Resource Limits**: Free tier has 512MB RAM and limited CPU time
- **No Custom Domain**: Free tier uses `yourusername.pythonanywhere.com`

### Troubleshooting

- **Check error logs**: Go to "Web" tab → "Error log"
- **Check server log**: Go to "Web" tab → "Server log"
- **Reload the app**: Click "Reload" button after making changes
- **Virtualenv issues**: Reinstall dependencies in the virtualenv

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
