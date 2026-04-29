# Deploy Nexus AI to Koyeb

This plan deploys your FastAPI chatbot to Koyeb's free tier.

## Koyeb Free Tier Limitations
- **Completely free** - no credit card required
- **512MB RAM** - may be insufficient for full version with embeddings
- **Sleep mode** - apps sleep after inactivity, wake on request
- **Git-based deployment** - auto-deploy on push to GitHub
- **Custom domains** - available on paid plans only

## Deployment Steps

### 1. Push Code to GitHub
```bash
git add .
git commit -m "Ready for Koyeb deployment"
git push origin main
```

### 2. Sign Up at Koyeb
- Go to https://www.koyeb.com
- Create a free account using GitHub or email

### 3. Create New App
- Click "Create App"
- Select "GitHub" as source
- Connect your GitHub account
- Select your repository

### 4. Configure Build Settings
- **Builder**: Choose "Buildpacks" (auto-detects Python)
- **Python Version**: 3.10 or 3.11
- **Build Command**: (leave empty - auto-detected)
- **Run Command**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### 5. Set Environment Variables
Add these in the app settings:
- `GROQ_API_KEY`: Your Groq API key
- `LLM_PROVIDER`: `groq`
- `GROQ_MODEL`: `llama-3.3-70b-versatile`

### 6. Configure Port
- Expose port: `8000`
- Protocol: HTTP

### 7. Deploy
- Click "Deploy"
- Wait for build and deployment

### 8. Access Your App
- Koyeb provides a URL: `https://your-app.koyeb.app`
- Test the application

## Troubleshooting Memory Issues

If you get "Out of memory" errors:

1. **Use lightweight version:**
   - Change requirements to `requirements-light.txt`
   - Change run command to: `uvicorn src.main_light:app --host 0.0.0.0 --port 8000`

2. **Or upgrade to paid tier:**
   - Koyeb paid plans offer more RAM

## Important Notes
- Free tier has 512MB RAM limit
- Apps sleep after 30 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Auto-deploy on every push to main branch
