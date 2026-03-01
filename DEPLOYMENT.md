# Deployment Guide

Deploy the Agentic Customer Care AI for free using **Vercel** (frontend) and **Render** (backend).

```
User → Vercel (Next.js)
         │
         │  /api/* proxied
         ▼
       Render (FastAPI + SQLite)
         │
         └── OpenAI GPT-4o
```

---

## Prerequisites

- [GitHub](https://github.com) account
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Vercel](https://vercel.com) account (free — sign up with GitHub)
- [Render](https://render.com) account (free — sign up with GitHub)

---

## Step 1: Push to GitHub

If you haven't already, create a repo and push your code:

```bash
cd agentic-customer-care

git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/agentic-customer-care.git
git branch -M main
git push -u origin main
```

> **Important:** The `.env` file is in `.gitignore` — your API key will NOT be pushed. This is expected. You'll set it as an environment variable in Render.

---

## Step 2: Deploy Backend on Render

### 2.1 Create the Service

1. Go to [render.com/dashboard](https://render.com/dashboard)
2. Click **New** → **Web Service**
3. Select **Build and deploy from a Git repository** → Connect your GitHub repo
4. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `agentic-care-backend` |
| **Region** | Pick the closest to you |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Instance Type** | `Free` |

### 2.2 Set Environment Variables

Scroll down to **Environment Variables** and add these:

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | Your actual OpenAI key (`sk-proj-...`) |
| `PRIMARY_LLM` | `gpt-4o` |
| `FALLBACK_LLM` | `gpt-4o-mini` |
| `DATABASE_URL` | `sqlite:///./ecommerce.db` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | `https://agentic-customer-care.vercel.app` |

> **Note:** Update `CORS_ORIGINS` later with your actual Vercel URL if it differs.

### 2.3 Deploy

1. Click **Deploy Web Service**
2. Wait for the build to finish (takes ~2-3 minutes)
3. Once deployed, you'll get a URL like:
   ```
   https://agentic-care-backend.onrender.com
   ```
4. Verify it works by visiting:
   ```
   https://agentic-care-backend.onrender.com/api/health
   ```
   You should see a JSON health check response.

> **Note:** The database auto-seeds with demo data (5 users, 25 products, 18 orders) on first startup.

---

## Step 3: Deploy Frontend on Vercel

### 3.1 Create the Project

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click **Add New...** → **Project**
3. Select **Import Git Repository** → Choose your repo

### 3.2 Configure the Project

| Setting | Value |
|---------|-------|
| **Framework Preset** | `Next.js` (auto-detected) |
| **Root Directory** | Click **Edit** → type `frontend` → Click **Continue** |

### 3.3 Set Environment Variable

Under **Environment Variables**, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://agentic-care-backend.onrender.com` |

> Replace with your actual Render backend URL from Step 2.3.

### 3.4 Deploy

1. Click **Deploy**
2. Wait for the build (~1-2 minutes)
3. Your app is live! Vercel gives you a URL like:
   ```
   https://agentic-customer-care.vercel.app
   ```

---

## Step 4: Update CORS (Final Step)

Go back to **Render Dashboard** → your backend service → **Environment**:

Update `CORS_ORIGINS` with your actual Vercel URL:

```
https://agentic-customer-care.vercel.app
```

Render will auto-redeploy with the new setting.

---

## Verify Everything Works

1. Open your Vercel URL in the browser
2. Type "Hello" in the chat → You should get a greeting from the Router agent
3. Try "Show me my orders" → Order Tracker should list orders
4. Try "I want to return the Garmin Watch from ORD-2025-00001" → Returns Specialist should check eligibility

---

## Cost Summary

| Service | Plan | Cost |
|---------|------|:----:|
| Vercel | Hobby | **$0** |
| Render | Free | **$0** |
| OpenAI | Pay-as-you-go | **~$0.01-0.05 per conversation** |

Typical demo usage (50-100 conversations/month): **< $2/month** total.

---

## Common Issues

### Backend takes 30+ seconds to respond on first request

Render's free tier **spins down after 15 minutes of inactivity**. The first request after sleep triggers a cold start (~30 seconds). This is normal. Subsequent requests are fast.

**Workaround:** Use [UptimeRobot](https://uptimerobot.com) (free) to ping your backend's `/api/health` endpoint every 14 minutes to keep it awake.

### CORS Error in Browser Console

```
Access to fetch has been blocked by CORS policy
```

Your `CORS_ORIGINS` env var in Render doesn't match your Vercel URL. Go to Render → Environment → update it. Make sure there are no trailing slashes.

### "I'm experiencing technical difficulties"

This means the LLM call failed. Check:
1. Render logs (Dashboard → Logs) for the actual error
2. Most common cause: `OPENAI_API_KEY` not set or invalid
3. Verify key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Database is Empty / No Orders

The database auto-seeds on first startup if it detects no users. If it didn't seed:
1. Go to Render Dashboard → your service → **Shell**
2. Run:
   ```bash
   python -m app.db.seed
   ```

### Frontend Shows Blank / API Errors

Check that `NEXT_PUBLIC_API_URL` in Vercel matches your Render URL exactly. After changing it, **redeploy** the frontend (Vercel Dashboard → Deployments → Redeploy).

---

## Custom Domain (Optional)

### Frontend (Vercel)
1. Vercel Dashboard → your project → **Settings** → **Domains**
2. Add your domain (e.g., `care.yourdomain.com`)
3. Point your DNS CNAME to `cname.vercel-dns.com`

### Backend (Render)
1. Render Dashboard → your service → **Settings** → **Custom Domain**
2. Add your domain (e.g., `api.yourdomain.com`)
3. Follow Render's DNS instructions
4. Update `CORS_ORIGINS` to include the new frontend domain
5. Update `NEXT_PUBLIC_API_URL` in Vercel to the new backend domain

---

## Architecture in Production

```
┌─────────────────────────────────────────────────────┐
│                  VERCEL (Free)                       │
│                                                     │
│  Next.js 16 Frontend                                │
│  - Static + SSR pages                               │
│  - API rewrites → Render backend                    │
│  - Global CDN edge network                          │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────────┐
│                  RENDER (Free)                       │
│                                                     │
│  Docker Container                                   │
│  ├── FastAPI (Python 3.11)                          │
│  ├── LangGraph Multi-Agent System                   │
│  │   ├── Router Agent (intent classification)       │
│  │   ├── Product Specialist                         │
│  │   ├── Order Tracker                              │
│  │   ├── Returns Specialist                         │
│  │   └── Escalation Handler                         │
│  ├── SQLite Database (auto-seeded)                  │
│  └── Guardrails (input/output validation)           │
│                                                     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────────┐
│              OPENAI API (Pay-as-you-go)             │
│                                                     │
│  Primary:  GPT-4o                                   │
│  Fallback: GPT-4o-mini                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Updating After Code Changes

### Backend
Push to GitHub → Render auto-deploys from `main` branch.

### Frontend
Push to GitHub → Vercel auto-deploys from `main` branch.

Both platforms support **automatic deployments** on every push. No manual action needed.
