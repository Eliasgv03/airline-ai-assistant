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

### LLM Layer
- **Gemini**: Primary LLM provider
- **Groq**: Fallback LLM provider
- **Model Pool**: Multiple models with automatic fallback

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
