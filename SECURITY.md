# 🔐 Security & Environment Setup Instructions

## ⚠️ IMPORTANT: Environment Variables Setup

Your `.env` file has been removed from git for security reasons. To run the application:

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your actual API keys:**
   ```bash
   # Get your Groq API key from: https://console.groq.com/
   GROQ_API_KEY="your_actual_groq_api_key_here"
   
   # Get your Hugging Face token from: https://huggingface.co/settings/tokens
   HUGGINGFACEHUB_API_TOKEN="your_actual_huggingface_token_here"
   ```

## 🚀 Quick Start

1. Clone the repository
2. Set up your environment variables (see above)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python web_app.py`

## 🔒 Security Best Practices

- ✅ `.env` file is in `.gitignore` - never commit API keys
- ✅ Use environment variables for all secrets
- ✅ Regularly rotate your API keys
- ✅ Use different keys for development and production

## 📝 Note for Developers

If you need to add new environment variables:
1. Add them to `.env.example` with placeholder values
2. Add them to your local `.env` with actual values
3. **NEVER** commit the actual `.env` file

## 🛠️ Production Deployment

For production, set environment variables through your hosting platform:
- Docker: Use `-e` flags or environment files
- Kubernetes: Use ConfigMaps and Secrets
- Cloud platforms: Use their environment variable settings