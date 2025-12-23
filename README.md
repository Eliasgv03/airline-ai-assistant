# Airline AI Assistant ✈️ 🤖

An AI-powered airline chatbot inspired by Air India's "Maharaja". Built for the AI Champions technical assessment.

![Status](https://img.shields.io/badge/Status-Development-yellow)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20LangChain-blue)

## 📋 Project Overview

This monorepo contains:
- **`backend/`**: FastAPI service with LangChain, **FAISS (Vector Store)**, and Groq integration.
- **`frontend/`**: Next.js 14 application with Tailwind CSS and shadcn/ui.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Groq API Key](https://console.groq.com/) (Free)

### 1. Environment Setup

```bash
# Backend (.env)
cd backend
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

```bash
# Frontend (.env.local)
cd frontend
echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" > .env.local
```

### 2. Backend Setup (Python)

```bash
cd backend
# Install dependencies (using poetry)
poetry install

# Run server
poetry run uvicorn app.main:app --reload
```
*API will be available at http://localhost:8000/docs*

### 3. Frontend Setup (Next.js)

```bash
cd frontend
# Install dependencies
npm install

# Run development server
npm run dev
```
*Frontend will be available at http://localhost:3000*

## 🛠️ Architecture

- **LLM**: Meta LLaMA 3 70B (via Groq)
- **Vector Store**: FAISS (CPU optimized for local dev)
- **Frontend**: Client-side chat interface with streaming support
- **Infrastructure**: Ready for deployment on Render.com

## 📝 License

This project is part of a technical evaluation.
