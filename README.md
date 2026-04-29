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

## Deployment to Render.com

### Prerequisites
- Render.com account (free tier)
- Git repository (GitHub, GitLab, or Bitbucket)
- GROQ_API_KEY from https://console.groq.com

### Step-by-Step Deployment

1. **Push code to Git:**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Sign up at Render.com:**
   - Go to https://render.com
   - Create a free account using GitHub/GitLab/Bitbucket

3. **Create a new Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Connect your Git repository
   - Select the repository containing your project

4. **Configure the Web Service:**
   - **Name**: nexus-ai (or any name you prefer)
   - **Region**: Choose nearest region
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free (512MB RAM, 0.1 CPU)

5. **Set Environment Variables:**
   - Scroll to "Environment Variables" section
   - Add:
     - `GROQ_API_KEY`: Your Groq API key
     - `LLM_PROVIDER`: `groq`
     - `GROQ_MODEL`: `llama-3.3-70b-versatile`

6. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for the deployment to complete (check the "Logs" tab)

7. **Access your app:**
   - Once deployed, Render will provide a URL like: `https://nexus-ai.onrender.com`
   - Visit the URL to test your application

### Important Notes

- **Ephemeral Storage**: Uploaded files are lost when the app redeploys or restarts
- **Sleep Mode**: Free tier services spin down after 15 minutes of inactivity (wakes on first request, may take 30-60 seconds)
- **Resource Limits**: Free tier has 512MB RAM and 0.1 CPU
- **Build Time**: Free tier has limited build time (15 minutes per build)
- **Custom Domain**: Available on paid plans only

### Troubleshooting

- **Check logs**: Go to your service → "Logs" tab
- **Redeploy**: Click "Manual Deploy" → "Clear build cache & deploy"
- **Environment variables**: Ensure all required variables are set
- **Build failures**: Check the "Build Log" for dependency installation errors

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
