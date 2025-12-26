# 🚀 Deployment Guide - Step by Step (100% FREE)

## Overview

This guide will deploy your AI chatbot to production using:
- **Supabase**: PostgreSQL database (FREE)
- **Render**: Backend + Frontend hosting (FREE)
- **Auto-ingestion**: Data loads automatically on first deploy

**Total Cost**: $0/month
**Time**: ~15 minutes
**Credit Card**: NOT required

---

## Prerequisites

Before starting, have ready:
- [ ] GitHub account with your code pushed
- [ ] Groq API key (free from https://console.groq.com/keys)
- [ ] 15 minutes of time

---

## Step 1: Create Supabase Database (5 minutes)

### 1.1 Create Project

1. Go to https://supabase.com
2. Click **"Start your project"** → **"Sign in"**
3. Sign up with GitHub (free, no card needed)
4. Click **"New project"**
5. Fill in:
   - **Organization**: Create new or select existing
   - **Name**: `airline-ai-assistant`
   - **Database Password**: Create a strong password
     - **IMPORTANT**: Save this password! You'll need it.
   - **Region**: Choose closest to you (e.g., `US East (Ohio)`)
   - **Pricing Plan**: Free (selected by default)
6. Click **"Create new project"**
7. Wait ~2 minutes while it provisions

### 1.2 Enable pgvector Extension

1. In your project dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"+ New query"**
3. Paste this SQL:
   ```sql
   -- Enable vector extension for RAG
   CREATE EXTENSION IF NOT EXISTS vector;

   -- Verify it worked
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```
4. Click **"Run"** (or press Ctrl+Enter)
5. Should see `vector` in results ✅

### 1.3 Get Connection String

1. Click **"Settings"** (gear icon, left sidebar)
2. Click **"Database"**
3. Scroll to **"Connection string"** section
4. Click **"Connection Pooling"** tab (NOT "URI")
5. Mode: Select **"Transaction"**
6. Copy the connection string:
   ```
   postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
7. **IMPORTANT**: Replace `[YOUR-PASSWORD]` with your actual password
8. **Save this string** - you'll need it in Step 2

**✅ Supabase Setup Complete!**

---

## Step 2: Deploy Backend to Render (5 minutes)

### 2.1 Create Web Service

1. Go to https://dashboard.render.com
2. Sign up/login (free, **NO card needed**)
3. Click **"New +"** (top right) → **"Web Service"**
4. Click **"Build and deploy from a Git repository"** → **"Next"**
5. Click **"Connect account"** → Connect GitHub
6. Find your repository: `airline-ai-assistant`
7. Click **"Connect"**

### 2.2 Configure Service

Fill in the form:

**Name**:
```
airline-ai-assistant-backend
```

**Region**:
```
Oregon (US West)
```
(Or choose closest to you - same as Supabase if possible)

**Branch**:
```
main
```

**Root Directory**:
```
backend
```

**Runtime**:
```
Python 3
```

**Build Command**:
```bash
pip install poetry && poetry config virtualenvs.create false && poetry install --only main
```

**Start Command**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level info
```

**Instance Type**:
```
Free
```

### 2.3 Advanced Settings

Click **"Advanced"** to expand:

**Health Check Path**:
```
/health
```

**Auto-Deploy**:
```
Yes (checked)
```

### 2.4 Add Environment Variables

Scroll to **"Environment Variables"**, click **"Add Environment Variable"**:

**Variable 1** (Required):
- Key: `DATABASE_URL`
- Value: `<paste your Supabase connection string here>`

**Variable 2** (Required - choose one):
- Key: `GROQ_API_KEY`
- Value: `<your Groq API key>`

**Variable 3** (Recommended):
- Key: `LLM_PROVIDER`
- Value: `groq`

**Variable 4** (Recommended):
- Key: `ENVIRONMENT`
- Value: `production`

**Variable 5** (Recommended):
- Key: `LOG_LEVEL`
- Value: `info`

### 2.5 Create Service

1. Click **"Create Web Service"** (bottom)
2. Wait for build (~3-5 minutes)
3. Watch the logs - you'll see:
   ```
   Installing dependencies...
   Building...
   Starting server...
   🚀 Application starting up...
   🔍 Checking if data ingestion is needed...
   📭 Database appears empty
   🚀 Database is empty - starting automatic data ingestion...
   📦 This will take ~1-2 minutes...
   ✅ Auto-ingestion completed successfully!
   ✅ Application startup complete
   ```
4. When you see "Your service is live 🎉" → **Success!**
5. **Copy your backend URL** (top of page):
   ```
   https://airline-ai-assistant-backend.onrender.com
   ```

**✅ Backend Deployed!** Data ingestion ran automatically.

---

## Step 3: Deploy Frontend to Render (3 minutes)

### 3.1 Create Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Build and deploy from a Git repository"** → **"Next"**
3. Select **same repository**: `airline-ai-assistant`
4. Click **"Connect"**

### 3.2 Configure Service

**Name**:
```
airline-ai-assistant-frontend
```

**Region**:
```
Oregon (US West)
```
(SAME as backend!)

**Branch**:
```
main
```

**Root Directory**:
```
frontend
```

**Runtime**:
```
Node
```

**Build Command**:
```bash
npm install --production=false && npm run build
```

**Start Command**:
```bash
npm start
```

**Instance Type**:
```
Free
```

### 3.3 Add Environment Variable

**Variable 1** (Required):
- Key: `NEXT_PUBLIC_BACKEND_URL`
- Value: `https://airline-ai-assistant-backend.onrender.com`
  - **Replace with YOUR actual backend URL**
  - **NO trailing slash!**

**Variable 2** (Optional):
- Key: `NODE_ENV`
- Value: `production`

### 3.4 Create Service

1. Click **"Create Web Service"**
2. Wait for build (~2-3 minutes)
3. When done, you'll see "Your service is live 🎉"
4. **Copy your frontend URL**:
   ```
   https://airline-ai-assistant-frontend.onrender.com
   ```

**✅ Frontend Deployed!**

---

## Step 4: Verify Everything Works (2 minutes)

### 4.1 Test Backend

Open in browser or use curl:
```bash
https://airline-ai-assistant-backend.onrender.com/health
```

**Expected response**:
```json
{
  "status": "ok",
  "environment": "production"
}
```

✅ If you see this, backend is working!

### 4.2 Test Frontend

1. Open your frontend URL in browser:
   ```
   https://airline-ai-assistant-frontend.onrender.com
   ```
2. Should see chat interface
3. Type: **"What is the baggage allowance for international flights?"**
4. Wait ~5 seconds (first request is slow)
5. Should get detailed response about baggage policies ✅

### 4.3 Test Flight Search

Type: **"Find flights from Delhi to Mumbai tomorrow"**

Should see flight results with prices! ✈️

### 4.4 Test Multi-Language

Type: **"¿Cuál es el equipaje permitido?"** (Spanish)

Should respond in Spanish! 🌍

**✅ Everything works!**

---

## Step 5: What Happens on Redeployments?

### Smart Auto-Ingestion

The system is **smart** - it checks if data exists:

**First deploy**:
```
🔍 Checking if data ingestion is needed...
📭 Database appears empty
🚀 Starting automatic data ingestion...
✅ Auto-ingestion completed!
```

**Subsequent deploys**:
```
🔍 Checking if data ingestion is needed...
✅ Database already populated - skipping ingestion
ℹ️ This prevents duplicate data on redeployments
```

**No duplicates!** Data ingests only once. ✨

---

## Troubleshooting

### Backend won't start

**Check logs** (Render → Backend → Logs):

**Problem**: `Database connection failed`
- **Fix**: Check `DATABASE_URL` is correct
- Verify Supabase connection string
- Make sure password is correct

**Problem**: `API key not configured`
- **Fix**: Add `GROQ_API_KEY` in environment variables

**Problem**: Build fails
- **Fix**: Check `backend` is in Root Directory
- Verify build command is correct

### Frontend can't connect

**Problem**: Chat doesn't respond
- **Fix**: Check `NEXT_PUBLIC_BACKEND_URL` in frontend env vars
- Must be exact backend URL
- NO trailing slash
- Must start with `https://`

**Problem**: CORS error in browser console
- **Fix**: Backend CORS is already configured
- Make sure both services deployed successfully
- Try hard refresh (Ctrl+Shift+R)

### Data ingestion didn't run

**Check backend logs** for:
```
🚀 Database is empty - starting automatic data ingestion...
```

**If you don't see it**:

**Option 1**: Redeploy backend
- Render → Backend → Manual Deploy → "Clear build cache & deploy"

**Option 2**: Run manually from your computer
```bash
export DATABASE_URL="your-supabase-url"
cd backend
poetry run python -m app.scripts.ingest_data
```

### Services keep sleeping

**This is normal on free tier!**
- Services sleep after 15 min of inactivity
- First request takes ~30 seconds to wake up
- Subsequent requests are fast

**Solutions**:
- Accept it (fine for demo/portfolio)
- Use cron-job.org to ping every 14 min (free)
- Upgrade to paid tier ($7/month per service)

---

## Viewing Logs

### Real-Time Logs

1. Render Dashboard → Your service
2. Click **"Logs"** tab
3. See real-time output with emojis:
   ```
   🔵 [1234567890] POST /api/chat from 1.2.3.4
   ✅ [1234567890] POST /api/chat → 200 (1234.56ms)
   ```

### Search Logs

- Use search box to find specific messages
- Filter by time
- Download logs if needed

---

## Cost Breakdown

**Total: $0/month** 🎉

| Service | Plan | Cost |
|---------|------|------|
| Render Backend | Free (750 hrs/mo) | $0 |
| Render Frontend | Free (750 hrs/mo) | $0 |
| Supabase Database | Free (500MB) | $0 |
| Groq API | Free (14,400 req/day) | $0 |

**Perfect for**:
- ✅ Portfolio projects
- ✅ Technical assessments
- ✅ Demos
- ✅ Learning

---

## Next Steps

### 1. Update README

Add your live URLs:
```markdown
## 🌐 Live Demo

- **Frontend**: https://airline-ai-assistant-frontend.onrender.com
- **Backend API**: https://airline-ai-assistant-backend.onrender.com/docs
```

### 2. Take Screenshots

For your README:
- Chat interface
- RAG response example
- Flight search results
- Multi-language support

### 3. Test Thoroughly

Try different queries:
- Policy questions
- Flight searches
- Different languages
- Edge cases

### 4. Monitor

- Check logs occasionally
- Watch for errors
- Monitor Supabase usage

### 5. Share!

Add to:
- Your resume
- LinkedIn
- Portfolio website
- GitHub profile

---

## Deployment Checklist

- [ ] Supabase project created
- [ ] pgvector extension enabled
- [ ] Connection string saved
- [ ] Backend deployed to Render
- [ ] Backend env vars configured
- [ ] Backend health check works
- [ ] Auto-ingestion ran successfully
- [ ] Frontend deployed to Render
- [ ] Frontend env var configured
- [ ] Frontend loads in browser
- [ ] Chat responds to messages
- [ ] RAG queries work
- [ ] Flight search works
- [ ] Multi-language works
- [ ] URLs saved for README

---

## Support

**Render**:
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Community: https://community.render.com

**Supabase**:
- Dashboard: https://app.supabase.com
- Docs: https://supabase.com/docs
- Discord: https://discord.supabase.com

**Issues?**
- Check logs first
- See `LOGGING_AND_DEBUGGING.md`
- Review this guide

---

## 🎉 Congratulations!

Your AI chatbot is now **live and accessible worldwide**!

You just deployed a production AI application with:
- ✅ RAG system (pgvector)
- ✅ LLM integration (Groq)
- ✅ Real-time streaming
- ✅ Multi-language support
- ✅ Flight search
- ✅ Auto-scaling infrastructure

**All for $0/month!** 🚀

Share your project and be proud! �
