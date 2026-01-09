# Project Structure

```
advanced-rag-system/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration settings
│   │   └── database.py              # Database connection and session management
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py                # SQLAlchemy models (User, Document, etc.)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication endpoints
│   │   ├── documents.py             # Document management endpoints
│   │   └── chat.py                  # Chat endpoints
│   │
│   └── services/
│       ├── __init__.py
│       ├── vector_store.py          # Vector store management (ChromaDB/FAISS)
│       ├── rag_pipeline.py          # Advanced RAG pipeline (HyDE, Hybrid, Rerank)
│       ├── document_processor.py    # Document processing with vision parsing
│       └── chat_service.py          # Chat service with agentic orchestration
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_documents.py
│   ├── test_chat.py
│   └── test_rag_pipeline.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── uploads/                         # User uploaded documents (gitignored)
├── logs/                            # Application logs (gitignored)
├── faiss_index/                     # FAISS index storage (gitignored)
│
├── docker-compose.yml               # Docker Compose configuration
├── Dockerfile                       # Docker container definition
├── requirements.txt                 # Python dependencies
├── .env.template                    # Environment variables template
├── .env                             # Environment variables (gitignored)
├── .gitignore
├── README.md                        # Main documentation
├── PROJECT_STRUCTURE.md             # This file
├── test_client.py                   # WebSocket test client
└── alembic.ini                      # Alembic configuration
```

## Component Responsibilities

### Core Components

#### `app/main.py`
- FastAPI application initialization
- Middleware configuration
- Router registration
- WebSocket endpoint for real-time chat
- Lifecycle management (startup/shutdown)

#### `app/core/config.py`
- Centralized configuration using Pydantic Settings
- Environment variable management
- Model settings (embedding, chat, reasoning, vision)
- RAG configuration (chunk size, top-k, HyDE, etc.)

#### `app/core/database.py`
- Async SQLAlchemy engine setup
- Session management
- Database initialization

### Models

#### `app/models/models.py`
- `User`: User accounts and authentication
- `Document`: Uploaded document metadata
- `DocumentChunk`: Individual document chunks with embeddings
- `Conversation`: Chat conversations
- `Message`: Individual messages in conversations

### API Endpoints

#### `app/api/auth.py`
- `POST /register`: User registration
- `POST /token`: Login and JWT token generation
- `GET /me`: Get current user info
- JWT authentication middleware

#### `app/api/documents.py`
- `POST /upload`: Upload and process documents
- `GET /`: List user's documents
- `GET /{id}`: Get document details
- `DELETE /{id}`: Delete document

#### `app/api/chat.py`
- `POST /query`: Non-streaming chat query
- `GET /conversations`: List conversations
- `GET /conversations/{id}`: Get conversation details
- `DELETE /conversations/{id}`: Delete conversation

### Services

#### `app/services/vector_store.py`
**VectorStoreManager** - Manages vector databases
- Supports both ChromaDB (production) and FAISS (demo)
- Embedding generation via OpenAI
- Similarity search (dense retrieval)
- Keyword search (sparse retrieval)
- Document CRUD operations

#### `app/services/rag_pipeline.py`
**AdvancedRAGPipeline** - Implements advanced RAG techniques
1. **Query Optimization (HyDE)**
   - Generates hypothetical documents
   - Improves retrieval for ambiguous queries
   
2. **Hybrid Search**
   - Combines dense (vector) and sparse (keyword) search
   - Reciprocal Rank Fusion (RRF) for result combination
   
3. **LLM Reranking**
   - Uses LLM to score relevance
   - Improves precision of top results

#### `app/services/document_processor.py`
**DocumentProcessor** - Processes uploaded documents
- Vision-based parsing using GPT-4.1-mini
- Handles complex structures (tables, headers)
- Smart chunking with overlap
- Multi-format support (PDF, DOCX, TXT, MD)

#### `app/services/chat_service.py`
**ChatService** - Agentic chat orchestration
- Dynamic workflow planning using OpenAI agents
- Tool calling for RAG components
- Streaming response generation
- Conversation history management
- Optional o3 reasoning model usage

## Data Flow

### Document Upload Flow
```
1. User uploads document via API
   ↓
2. DocumentProcessor extracts and chunks text
   ↓
3. Chunks embedded via OpenAI API
   ↓
4. Embeddings stored in ChromaDB/FAISS
   ↓
5. Metadata stored in PostgreSQL
```

### Chat Query Flow
```
1. User sends query via WebSocket/API
   ↓
2. Agent plans workflow (needs retrieval? use HyDE? etc.)
   ↓
3. RAG Pipeline executes:
   a. Query Optimization (HyDE)
   b. Hybrid Search (Dense + Sparse + RRF)
   c. LLM Reranking
   ↓
4. Retrieved docs used to generate response
   ↓
5. Response streamed back to user
   ↓
6. Conversation saved to database
```

## Technology Stack

### Backend
- **FastAPI**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM
- **PostgreSQL 16**: Relational database
- **Uvicorn**: ASGI server

### Vector Stores
- **ChromaDB**: Production vector database
- **FAISS**: Demo/local vector database

### AI/ML
- **OpenAI API**: Embeddings, chat, reasoning, vision
  - `text-embedding-3-small`: Embeddings
  - `gpt-4o-mini`: General chat and vision
  - `o1-mini`: Reasoning for complex queries
- **LangChain**: RAG utilities and demonstrations

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Configuration

### Environment Variables

See `.env.template` for all configuration options:
- OpenAI API credentials
- Database connection strings
- Model selections
- RAG hyperparameters
- Security settings

### RAG Tuning Parameters

Key parameters for tuning RAG performance:
- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RETRIEVAL`: Number of docs to retrieve (default: 10)
- `RERANK_TOP_K`: Number of docs after reranking (default: 5)
- `HYDE_NUM_HYPOTHETICAL_DOCS`: HyDE docs to generate (default: 3)
- `HYBRID_SEARCH_ALPHA`: Dense/sparse balance (default: 0.5)

## Development Guidelines

### Adding New Features

1. **New Endpoint**: Add to appropriate router in `app/api/`
2. **New Service**: Create in `app/services/`
3. **New Model**: Add to `app/models/models.py`
4. **Database Changes**: Create Alembic migration

### Testing

Create tests in `tests/` directory:
- Use pytest and pytest-asyncio
- Mock external API calls
- Test both success and error cases

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions/classes
- Use async/await for I/O operations

## Deployment

### Production Checklist

- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use production OpenAI models
- [ ] Configure proper logging
- [ ] Set up database backups
- [ ] Enable HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up monitoring (e.g., Prometheus)
- [ ] Use persistent volumes for data
- [ ] Configure proper CORS settings
- [ ] Review and adjust resource limits

### Scaling Considerations

- Use Redis for caching and session management
- Implement task queue (Celery) for document processing
- Use CDN for static assets
- Consider horizontal scaling with load balancer
- Implement proper database connection pooling
- Use read replicas for PostgreSQL

## Monitoring and Debugging

### Logs
- Application logs: `logs/app.log`
- Docker logs: `docker-compose logs -f`

### Database
- Connect to PostgreSQL: `docker exec -it rag_postgres psql -U rag_user -d rag_db`

### Vector Store
- ChromaDB UI: `http://localhost:8000`
- FAISS: Check `faiss_index/` directory

## Common Issues and Solutions

See README.md Troubleshooting section for common issues.