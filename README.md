# Airline AI Assistant ✈️ 🤖

An AI-powered airline chatbot inspired by Air India's "Maharaja". Built for the AI Champions technical assessment.

![Status](https://img.shields.io/badge/Status-Production-green)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20LangChain-blue)

## 🌐 Live Demo

- **Frontend**: [https://airline-ai-assistant-1.onrender.com](https://airline-ai-assistant-1.onrender.com)
- **Backend API**: [https://airline-ai-assistant.onrender.com/docs](https://airline-ai-assistant.onrender.com/docs)

---

## ✅ Requirements Completed

### Core Requirements (Must Complete) - 6/6 ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Web Interface | ✅ | Next.js 14 with Tailwind CSS, dark/light theme, responsive |
| LLM Integration | ✅ | Multi-provider (Gemini + Groq) with automatic fallback |
| Conversation Context | ✅ | Session-based memory with full conversation history |
| Air India Persona | ✅ | "Maharaja Assistant" with multilingual support |
| Live Deployment | ✅ | Deployed on Render.com (frontend + backend + database) |
| Documentation | ✅ | This README with setup instructions |

### Expected Requirements (Should Complete) - 3/3 ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| RAG System | ✅ | PostgreSQL + pgvector with 8 policy documents |
| Flight Search | ✅ | Amadeus API integration with mock data fallback |
| Intent Handling | ✅ | LangChain tool-based routing (policy vs flight search) |

### Bonus Features - 5/6 ⭐

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Streaming Responses | ✅ | Server-Sent Events (SSE) for real-time streaming |
| Multi-language | ✅ | English, Hindi, Spanish, Portuguese, French + Lingua auto-detection (95%+ accuracy) |
| Real Air India Data | ✅ | 8 policy documents (baggage, cancellation, check-in, etc.) |
| Professional UI | ✅ | Air India branding, welcome screen, flight cards |
| Error Handling | ✅ | Graceful fallbacks, cross-provider LLM fallback |
| Benchmarks | ✅ | 19 automated tests, 89.5% pass rate, multilingual + identity + boundary tests |

---

## 🛠️ Tech Stack & Rationale

### Backend

| Technology | Why This Choice |
|------------|-----------------|
| **FastAPI** | Modern async Python framework, automatic OpenAPI docs, excellent performance |
| **LangChain** | Battle-tested LLM orchestration, tool binding, RAG support |
| **PostgreSQL + pgvector** | Production-ready vector store, SQL operations, Render integration |
| **Google Gemini** | **Primary LLM** - Latest models, multimodal, tool calling support |
| **Groq** | **Fallback LLM** - Fast inference (30 RPM), auto-failover when Gemini unavailable |
| **Lingua** | Language detection with 95%+ accuracy, replaces langdetect |
| **Poetry** | Dependency management with lockfile for reproducibility |

### Frontend

| Technology | Why This Choice |
|------------|-----------------|
| **Next.js 14** | React framework with App Router, server components |
| **Tailwind CSS** | Utility-first CSS, rapid prototyping, consistent design |
| **TypeScript** | Type safety, better IDE support, fewer runtime errors |

### Infrastructure

| Technology | Why This Choice |
|------------|-----------------|
| **Render.com** | Free tier, managed PostgreSQL, easy deployment |
| **Docker** | Containerized database for local development |

---

## 🎯 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **PostgreSQL + pgvector** | Native vector support, production-ready persistence, SQL queries, easy integration with Render/Supabase |
| **Poetry** | Modern dependency management, lockfile for reproducibility, virtual environment handling |
| **Render.com** | Free tier with managed PostgreSQL, automatic deploys from GitHub, easy scaling |
| **Supabase** | Managed PostgreSQL with pgvector extension, connection pooling, dashboard for debugging |
| **Multi-LLM (Gemini + Groq)** | Reliability through fallback chain, handles API rate limits gracefully |
| **LangChain Tools** | Let LLM decide intent via tool binding instead of manual classification |
| **Server-Sent Events** | Simpler than WebSockets for one-way streaming, native browser support |
| **In-Memory Sessions** | Simple implementation suitable for demo, avoids Redis complexity |

---

## ⚠️ Known Limitations

1. **API Rate Limits**: Gemini free tier has strict limits (20 RPD). Groq recommended for production.
2. **Memory Persistence**: Session history lost on server restart (in-memory storage).
3. **Mock Flight Data**: Amadeus API requires production credentials for real flights.

---

## 📊 Benchmark Results

Run: `poetry run python -m app.scripts.benchmark_chatbot`

### Summary
| Metric | Value |
|--------|-------|
| **Pass Rate** | 89.5% (17/19 tests) |
| **Avg Latency** | 4.7s |
| **Avg Accuracy** | 93.4% |

### By Category
| Category | Tests | Pass Rate | Avg Latency |
|----------|-------|-----------|-------------|
| Policy | 8 | 87.5% | 4.3s |
| Tool Use | 2 | 100% | 9.8s |
| FAQ | 2 | 100% | 2.8s |
| Multilingual | 3 | 100% | 5.5s |
| Identity | 2 | 100% | 2.5s |
| Boundary | 2 | 50% | 4.0s |

### Failed Tests (2)
| Query | Reason | Latency |
|-------|--------|---------|
| "Benefits of Platinum status?" | ⏱️ Latency (11.5s > 5s limit) | 11,509ms |
| "Can you book a hotel for me?" | ⏱️ Latency (6.0s > 5s limit) | 6,007ms |

> **Note**: Both failures are due to API latency variability, not accuracy issues. The chatbot responded correctly in both cases.

---

## 🚀 Future Improvements

1. **Redis for Session Storage**: Persist conversations across restarts
2. **Production Flight API**: Full Amadeus integration with real-time data
3. **Voice Input/Output**: Speech-to-text and text-to-speech support
4. **Booking Flow**: Actually complete flight bookings (not just search)
5. **Analytics Dashboard**: Track usage, popular queries, satisfaction

---

## 📋 Project Structure

```
airline-ai-assistant/
├── backend/
│   ├── app/
│   │   ├── api/           # REST endpoints (chat, flights)
│   │   ├── core/          # Configuration
│   │   ├── services/      # Business logic (chat, LLM, RAG)
│   │   ├── tools/         # LangChain tools (flight search)
│   │   ├── prompts/       # System prompts
│   │   └── models/        # Pydantic schemas
│   ├── data/
│   │   └── policies/      # RAG knowledge base (8 docs)
│   └── tests/             # Test suite
├── frontend/
│   └── src/
│       ├── app/           # Next.js App Router
│       ├── components/    # React components
│       └── lib/           # API client
└── docs/                  # Additional documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for PostgreSQL with pgvector)
- API Key: [Groq](https://console.groq.com/keys) (recommended) or [Google AI](https://makersuite.google.com/app/apikey)

### Prerequisites

- **Tools**:
  - [Git](https://git-scm.com/downloads) (for version control)
  - [Docker](https://www.docker.com/products/docker-desktop/) (for PostgreSQL + pgvector)
  - [Python 3.11+](https://www.python.org/downloads/) (Backend runtime)
  - [Node.js 18+](https://nodejs.org/en/download/) (Frontend runtime)
- **Package Managers**:
  - **Poetry** (Python): `pip install poetry`
  - **npm** (Node.js): Included with Node.js
- **API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey) (Free)

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/Eliasgv03/airline-ai-assistant.git
cd airline-ai-assistant
```

### 2. Database Setup (Docker)

Start a local PostgreSQL instance with pgvector support:

```bash
# Start container
docker run -d \
  --name airline-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=airline_ai \
  -p 5432:5432 \
  ankane/pgvector:latest

# Enable pgvector extension inside the container
docker exec -it airline-postgres psql -U postgres -d airline_ai -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 3. Backend Setup

```bash
cd backend

# Install project dependencies with Poetry
poetry install

# Create configuration file
cat > .env << EOF
# Application Config
ENVIRONMENT=development
LOG_LEVEL=info
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/airline_ai

# LLM Configuration (Gemini as Primary)
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Groq as fallback
GROQ_API_KEY=your_groq_api_key_here
EOF

# Start the dev server
poetry run uvicorn app.main:app --reload
```

Server will be running at: `http://localhost:8000`
Docs available at: `http://localhost:8000/docs`

### 4. Frontend Setup

Open a new terminal session:

```bash
cd frontend

# Install Node.js dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

App will be available at: `http://localhost:3000`

### 5. Ingest Knowledge Base (Optional)

Populate the vector database with the policy documents:

```bash
cd backend
poetry run python -m app.scripts.ingest_data
```

---

## 🧪 Testing

```bash
cd backend

# Run unit tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test
poetry run pytest tests/test_api.py -v
```

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/` | POST | Send message, get response |
| `/api/chat/stream` | POST | Send message, stream response (SSE) |
| `/api/flights/search` | GET | Search flights by route |
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |

---

## 📝 License

This project is part of a technical evaluation for AI Champions.

---

## 👤 Author

Built by Carlos Elías González for the AI Champions AI Engineer position.
