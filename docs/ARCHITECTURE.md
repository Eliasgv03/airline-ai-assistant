# System Architecture

## Overview

The Airline AI Assistant is a conversational AI system built with a microservices-inspired architecture, featuring a FastAPI backend and Next.js frontend.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Chat UI     │  │ Theme       │  │ Streaming Handler       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/SSE
┌────────────────────────────▼────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Chat Service                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐  │   │
│  │  │ Memory     │  │ RAG        │  │ LLM Manager        │  │   │
│  │  │ Service    │  │ (pgvector) │  │ (Gemini/Groq)      │  │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │              LangChain Tools                        │  │   │
│  │  │  ┌─────────────┐  ┌──────────────────────────────┐ │  │   │
│  │  │  │ Flight      │  │ Flight Details               │ │  │   │
│  │  │  │ Search      │  │                              │ │  │   │
│  │  │  └─────────────┘  └──────────────────────────────┘ │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ PostgreSQL    │  │ Gemini API      │  │ Amadeus API     │
│ + pgvector    │  │ / Groq API      │  │ (Flights)       │
└───────────────┘  └─────────────────┘  └─────────────────┘
```

## Component Details

### Frontend Layer
- **Next.js 14**: React framework with App Router
- **Streaming**: Server-Sent Events for real-time responses
- **Theming**: Dark/light mode with next-themes

### API Layer
- **FastAPI**: Async Python web framework
- **CORS**: Cross-origin support for frontend
- **SSE**: Streaming endpoint for chat responses

### Service Layer
- **ChatService**: Orchestrates conversation flow
- **MemoryService**: Session-based conversation history
- **VectorService**: RAG with pgvector
- **LanguageService**: Multi-language detection

### LLM Layer (Strategy Pattern)

The LLM layer uses the **Strategy Pattern** for provider abstraction:

```
chat_service.py
      ↓ uses
llm_manager.py  ←── Central dispatcher (reads LLM_PROVIDER from config)
      ↓ routes to
┌─────────────────┬─────────────────┬─────────────────┐
│ GeminiProvider  │ GroqProvider    │ OpenAIProvider  │
│ (primary)       │ (alternative)   │ (add later)     │
└─────────────────┴─────────────────┴─────────────────┘
```

**Design Patterns Used:**
- **Strategy Pattern**: Providers are interchangeable strategies
- **Facade Pattern**: `llm_manager` provides unified interface
- **Dependency Inversion**: `chat_service` depends on abstraction, not concrete providers

**Key Files:**
| File | Purpose |
|------|---------|
| `llm_base.py` | Interface all providers must implement |
| `llm_manager.py` | Central dispatcher - routes to active provider |
| `gemini_service.py` | Gemini with round-robin rotation |
| `groq_service.py` | Groq high-speed alternative |

**Gemini Round-Robin Rotation:**
```
Request 1 → gemini-2.5-flash-lite (PRIMARY API KEY)
Request 2 → gemini-2.5-flash-lite (FALLBACK API KEY)
Request 3 → gemini-2.5-flash (PRIMARY API KEY)
Request 4 → gemini-2.5-flash (FALLBACK API KEY)
Request 5 → (cycle repeats)
```

**To switch providers:** Set `LLM_PROVIDER=groq` in `.env`

**To add a new provider:**
1. Create `new_service.py` with `NewProvider` class
2. Register in `llm_manager.py`


### Data Layer
- **PostgreSQL + pgvector**: Vector embeddings storage
- **Policy Documents**: 8 markdown files for RAG
- **Mock Flight Data**: Fallback for Amadeus API

## Request Flow

1. User sends message via frontend
2. Backend receives POST to `/api/chat/stream`
3. ChatService detects language
4. VectorService retrieves relevant context
5. LLM generates response with tools
6. Response streams back via SSE
7. Frontend displays incrementally
