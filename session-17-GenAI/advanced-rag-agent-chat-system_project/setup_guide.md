# Setup Guide - Advanced RAG Agent Chat System

This guide will walk you through setting up the Advanced RAG Agent Chat System from scratch.

## Prerequisites

Before you begin, ensure you have:

1. **Docker & Docker Compose** installed
   - Docker Desktop (Mac/Windows): https://www.docker.com/products/docker-desktop
   - Docker Engine (Linux): https://docs.docker.com/engine/install/

2. **OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Create an API key
   - Ensure you have credits/billing set up

3. **Basic knowledge of:**
   - Command line/terminal
   - REST APIs
   - Python (optional, for customization)

## Step-by-Step Setup

### Step 1: Get the Code

```bash
# Clone the repository (or extract from zip)
cd advanced-rag-system

# Verify all files are present
ls -la
```

You should see:
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `.env.template`
- `app/` directory
- Other configuration files

### Step 2: Configure Environment

```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file
nano .env  # or use your preferred editor
```

**Required configuration:**
```bash
# Set your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Leave other settings as default for now
```

**Important:** Make sure to:
- Replace `your_openai_api_key_here` with your actual key
- Change `your_secret_key_here_please_change_in_production` to a random string

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Quick Deploy (Recommended)

Use the deployment script:

```bash
# Make the script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh deploy
```

The script will:
1. Check Docker installation
2. Verify environment configuration
3. Create necessary directories
4. Build Docker containers
5. Start all services
6. Test the API

### Step 4: Manual Deploy (Alternative)

If you prefer manual control:

```bash
# Create necessary directories
mkdir -p uploads logs faiss_index

# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Step 5: Verify Installation

Test the API:

```bash
# Health check
curl http://localhost:8080/health

# Should return: {"status": "healthy"}
```

Access the interactive API documentation:
- Open browser: http://localhost:8080/docs

### Step 6: Create Your First User

#### Option A: Using curl

```bash
# Register a user
curl -X POST "http://localhost:8080/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "demo123"
  }'

# Login and get token
curl -X POST "http://localhost:8080/api/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo123"

# Save the token from the response
export TOKEN="your-token-here"
```

#### Option B: Using the API docs

1. Go to http://localhost:8080/docs
2. Click on `POST /api/auth/register`
3. Click "Try it out"
4. Fill in the user details
5. Click "Execute"
6. Repeat for `/api/auth/token` to get your access token

### Step 7: Upload Your First Document

```bash
# Using curl (replace with your actual token)
curl -X POST "http://localhost:8080/api/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/document.pdf"
```

Or use the API docs interface at http://localhost:8080/docs

### Step 8: Start Chatting

#### Option A: Using the test client (WebSocket)

```bash
# Install Python dependencies (if not already)
pip install websockets aiohttp

# Start interactive chat
python test_client.py
```

#### Option B: Using REST API

```bash
# Send a query
curl -X POST "http://localhost:8080/api/chat/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main topics in the uploaded document?"
  }'
```

## Common Setup Issues

### Issue: "Docker not found"

**Solution:**
```bash
# Install Docker Desktop or Docker Engine
# For Ubuntu:
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER
# Log out and back in
```

### Issue: "Port already in use"

**Solution:**
```bash
# Check what's using the ports
sudo lsof -i :8080  # API port
sudo lsof -i :5432  # PostgreSQL port
sudo lsof -i :8000  # ChromaDB port

# Stop conflicting services or change ports in docker-compose.yml
```

### Issue: "ChromaDB connection failed"

**Solution:**
```bash
# Restart ChromaDB
docker-compose restart chromadb

# Check logs
docker-compose logs chromadb

# Verify it's running
docker-compose ps
```

### Issue: "OpenAI API error"

**Solution:**
1. Verify your API key is correct in `.env`
2. Check you have credits: https://platform.openai.com/account/usage
3. Verify API key has proper permissions

### Issue: "Document upload fails"

**Solution:**
```bash
# Check file size (must be < 10MB by default)
ls -lh your-document.pdf

# Check file format is supported (.pdf, .txt, .docx, .md)

# Check logs for details
docker-compose logs backend
```

## Configuration Options

### Adjusting RAG Performance

Edit `.env` to tune RAG behavior:

```bash
# Increase retrieval size (more context, slower)
TOP_K_RETRIEVAL=15
RERANK_TOP_K=7

# Adjust chunking
CHUNK_SIZE=1500
CHUNK_OVERLAP=300

# Disable HyDE for faster queries
HYDE_ENABLED=False

# Change models for cost/performance tradeoff
CHAT_MODEL=gpt-3.5-turbo  # Cheaper but less capable
EMBEDDING_MODEL=text-embedding-3-large  # More accurate embeddings
```

After changing `.env`:
```bash
docker-compose restart backend
```

### Using FAISS Instead of ChromaDB

For local-only deployment without ChromaDB:

1. Edit `app/services/vector_store.py`
2. Change `VectorStoreManager(use_chroma=False)`
3. Rebuild: `docker-compose up -d --build`

### Switching Models

The system supports:
- **Chat Models**: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
- **Reasoning Models**: o1-mini, o1-preview
- **Embedding Models**: text-embedding-3-small, text-embedding-3-large

Edit `.env` and restart services.

## Development Setup

If you want to develop locally without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up local PostgreSQL
# Install PostgreSQL 16
# Create database: rag_db

# Set up local ChromaDB
pip install chromadb
chroma run --path ./chroma_data

# Run the application
uvicorn app.main:app --reload --port 8080
```

## Next Steps

Now that your system is set up:

1. **Read the README.md** for API documentation
2. **Explore PROJECT_STRUCTURE.md** to understand the codebase
3. **Try the advanced features:**
   - HyDE query optimization
   - Hybrid search
   - LLM reranking
   - Agentic orchestration

4. **Customize the system:**
   - Adjust RAG parameters
   - Add custom document processors
   - Implement custom retrieval strategies
   - Add monitoring and analytics

## Getting Help

If you encounter issues:

1. Check the logs:
   ```bash
   docker-compose logs -f backend
   ```

2. Check service status:
   ```bash
   docker-compose ps
   ```

3. Review the troubleshooting section in README.md

4. Check configuration in `.env`

## Production Deployment

Before deploying to production:

1. ✅ Set strong `SECRET_KEY`
2. ✅ Use production-grade models
3. ✅ Configure proper logging
4. ✅ Set up SSL/TLS
5. ✅ Configure backups
6. ✅ Set up monitoring
7. ✅ Review security settings
8. ✅ Configure rate limiting
9. ✅ Use persistent volumes
10. ✅ Set up CI/CD pipeline

See the "Production Deployment" section in README.md for details.

## Useful Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart a service
docker-compose restart [service_name]

# Rebuild after code changes
docker-compose up -d --build

# Access container shell
docker-compose exec backend bash

# Database shell
docker-compose exec postgres psql -U rag_user -d rag_db

# Run tests
docker-compose exec backend pytest

# Clean up everything
docker-compose down -v
```

---

**Congratulations!** 🎉 You now have a fully functional Advanced RAG Agent Chat System running!

For questions or issues, please refer to the documentation or create an issue on GitHub.