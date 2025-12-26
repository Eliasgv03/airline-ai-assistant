# Airline AI Assistant ✈️ 🤖

An AI-powered airline chatbot inspired by Air India's "Maharaja". Built for the AI Champions technical assessment.

![Status](https://img.shields.io/badge/Status-Development-yellow)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20LangChain-blue)

## 📋 Project Overview

This monorepo contains:
- **`backend/`**: FastAPI service with LangChain, **PostgreSQL + pgvector (Vector Store)**, and Gemini integration.
- **`frontend/`**: Next.js 14 application with Tailwind CSS and TypeScript.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for PostgreSQL with pgvector)
- [Google AI API Key](https://makersuite.google.com/app/apikey) (Free)

### 1. Database Setup (PostgreSQL + pgvector)

```bash
# Start PostgreSQL with pgvector using Docker
docker run -d \
  --name airline-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=airline_ai \
  -p 5432:5432 \
  ankane/pgvector:latest

# Enable pgvector extension
docker exec -it airline-postgres psql -U postgres -d airline_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

The database will be available at `localhost:5432` with:
- User: `postgres`
- Password: `postgres`
- Database: `airline_ai`

### 2. Environment Setup

```bash
# Backend (.env)
cd backend
# Create .env file with the following variables:
cat > .env << EOF
# Required
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/airline_ai
LLM_PROVIDER=groq  # or "gemini"
GROQ_API_KEY=your_groq_api_key_here  # Get from https://console.groq.com/keys
# OR
# GOOGLE_API_KEY=your_google_api_key_here  # Get from https://makersuite.google.com/app/apikey

# Optional
ENVIRONMENT=development
LOG_LEVEL=info
EOF
```

```bash
# Frontend (.env.local)
cd frontend
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
```

### 3. Backend Setup (Python)

```bash
cd backend
# Install dependencies (using poetry)
poetry install

# Run server
poetry run uvicorn app.main:app --reload
```
*API will be available at http://localhost:8000/docs*

### 4. Frontend Setup (Next.js)

```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm run dev
```
*Frontend will be available at http://localhost:3000*

### 5. Setup Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit hooks
cd backend
poetry run pre-commit install

# Run manually on all files (optional)
poetry run pre-commit run --all-files
```

This will automatically run code quality checks (ruff, mypy) before each commit.

## 🛠️ Architecture

- **LLM**: Google Gemini 1.5 Flash (via Google AI)
- **Vector Store**: PostgreSQL + pgvector (production-ready, persistent)
- **Framework**: LangChain 0.1.x for RAG orchestration
- **Frontend**: Client-side chat interface with streaming support
- **Infrastructure**: Ready for deployment on Render.com (managed PostgreSQL)

## 📚 Documentation

- [Implementation Plan](docs/implementation_plan.md) - Detailed development roadmap
- [API Documentation](http://localhost:8000/docs) - OpenAPI/Swagger (when backend is running)

## 🔄 Migration from FAISS to pgvector

This project uses **PostgreSQL + pgvector** instead of FAISS for:
- ✅ Production-ready persistence
- ✅ Scalable concurrent access
- ✅ Easy deployment on Render (managed database)
- ✅ Standard SQL operations

## 📝 License

This project is part of a technical evaluation.
