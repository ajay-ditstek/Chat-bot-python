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

### Option 1: Oracle Cloud Free Tier (Recommended - Up to 24GB RAM)

Oracle Cloud Free Tier offers the most resources for free deployment.

**Features:**
- ✅ Free chat with LLM
- ✅ Web search
- ✅ URL summarization
- ✅ PDF/image upload and document analysis
- ✅ Up to 24GB RAM (4 x 6GB instances)
- ✅ 200GB storage
- ✅ Always free (no sleep mode)

**Prerequisites:**
- Oracle Cloud account (free)
- SSH client
- Basic Linux command line knowledge
- GROQ_API_KEY from https://console.groq.com

**Step-by-Step Deployment:**

1. **Create Oracle Cloud Account:**
   - Go to https://www.oracle.com/cloud/free/
   - Sign up for free tier (requires credit card for verification, but no charges)

2. **Create a Compute Instance:**
   - Go to "Compute" → "Instances"
   - Click "Create Instance"
   - Name: `nexus-ai`
   - Compartment: Select your compartment
   - Shape: `VM.Standard.E2.1.Micro` (Always Free)
   - Operating System: `Oracle Linux` or `Ubuntu`
   - SSH Keys: Upload your public SSH key
   - Click "Create"

3. **SSH into the Instance:**
   ```bash
   ssh -i ~/.ssh/your-key opc@<your-instance-public-ip>
   ```

4. **Install Dependencies:**
   ```bash
   sudo yum update -y  # or sudo apt update for Ubuntu
   sudo yum install -y python3 python3-pip git
   ```

5. **Clone Your Repository:**
   ```bash
   git clone <your-github-repo-url>
   cd Chat-bot-python
   ```

6. **Create Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

7. **Set Environment Variables:**
   ```bash
   echo 'export GROQ_API_KEY="your-api-key"' >> ~/.bashrc
   echo 'export LLM_PROVIDER="groq"' >> ~/.bashrc
   echo 'export GROQ_MODEL="llama-3.3-70b-versatile"' >> ~/.bashrc
   source ~/.bashrc
   ```

8. **Run the Application:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

9. **Configure Security List (Firewall):**
   - Go to "Networking" → "Virtual Cloud Networks"
   - Select your VCN → Security Lists
   - Add Ingress Rule:
     - Source CIDR: `0.0.0.0/0`
     - Destination Port: `8000`
     - Protocol: TCP

10. **Access Your App:**
    - Visit `http://<your-instance-public-ip>:8000`

**Optional: Run as a Service (systemd):**
```bash
sudo nano /etc/systemd/system/nexus-ai.service
```

Add:
```ini
[Unit]
Description=Nexus AI
After=network.target

[Service]
User=opc
WorkingDirectory=/home/opc/Chat-bot-python
Environment="PATH=/home/opc/Chat-bot-python/venv/bin"
ExecStart=/home/opc/Chat-bot-python/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable nexus-ai
sudo systemctl start nexus-ai
```

### Option 2: Streamlit Cloud (Free with 1GB RAM)

Streamlit Cloud offers a free tier with 1GB RAM, but only for the lightweight version.

**Features:**
- ✅ Free chat with LLM
- ✅ Web search
- ✅ URL summarization
- ❌ No PDF/image upload (memory limited)
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

**Important Notes:**
- **Sleep Mode**: Free tier apps sleep after inactivity
- **Resource Limits**: Free tier has 1GB RAM
- **No document processing**: Lightweight version only

### Option 3: Render.com (Not Recommended - Only 512MB RAM)

Render.com's free tier has only 512MB RAM, which is insufficient for this app.

**If you still want to use Render.com:**
- You must use the lightweight version (`requirements-light.txt`, `src/main_light.py`)
- Even then, you may encounter out-of-memory errors
- Consider upgrading to Render's paid tier ($7/month for 1GB RAM)

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
