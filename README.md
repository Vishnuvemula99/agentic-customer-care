# Agentic Customer Care AI

An autonomous multi-agent customer service system for e-commerce, powered by LLMs and built with LangGraph. Five specialized AI agents collaborate to handle product inquiries, order tracking, returns processing, and escalation — all orchestrated through an intelligent routing system with built-in safety guardrails.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)
![React](https://img.shields.io/badge/React-19-61DAFB)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Multi-Agent System](#multi-agent-system)
- [Safety Guardrails](#safety-guardrails)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Database & Seed Data](#database--seed-data)
- [LLM Configuration](#llm-configuration)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Product Catalog](#product-catalog)
- [Return Policies](#return-policies)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16)                     │
│  Chat UI  ·  Agent Badges  ·  Markdown Rendering  ·  Sidebar    │
└────────────────────────────┬─────────────────────────────────────┘
                             │  HTTP (proxied via Next.js rewrites)
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                          │
│                                                                   │
│  ┌─────────────┐   ┌──────────────────────────────────────────┐  │
│  │   INPUT      │   │         LANGGRAPH STATE GRAPH            │  │
│  │  GUARDRAIL   │──▶│                                          │  │
│  │ - Injection  │   │  ┌────────────────────────────────┐      │  │
│  │ - Sanitize   │   │  │        ROUTER AGENT             │      │  │
│  │ - Length     │   │  │  Intent Classification (LLM)    │      │  │
│  └─────────────┘   │  │  Confidence Scoring              │      │  │
│                     │  └──────────┬───────────────────────┘      │  │
│                     │       ┌─────┼─────┬──────┬────────┐       │  │
│                     │       ▼     ▼     ▼      ▼        ▼       │  │
│                     │    Product Order Returns Escalation END    │  │
│                     │    Agent  Agent  Agent   Agent   (general) │  │
│                     │       │     │     │      │                 │  │
│                     │       └─────┴─────┴──────┘                 │  │
│                     │               │                            │  │
│                     └───────────────┼────────────────────────────┘  │
│                                     ▼                              │
│  ┌─────────────┐   ┌──────────────────────────────────────────┐  │
│  │   OUTPUT     │◀──│       TOOLS (DB-backed)                  │  │
│  │  GUARDRAIL   │   │  Orders · Products · Returns · Users     │  │
│  │ - PII Redact │   └──────────────────────────────────────────┘  │
│  │ - Policy     │                                                 │
│  └─────────────┘          ┌──────────────┐                       │
│                           │   SQLite DB   │                       │
│                           │  Users·Orders │                       │
│                           │  Products·etc │                       │
│                           └──────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent System

The system uses five specialized agents, each with dedicated tools and system prompts. The Router Agent classifies every incoming message and delegates to the right specialist.

### Agent Roster

| Agent | Role | Tools | When Activated |
|-------|------|-------|----------------|
| **Router** | Intent classification & routing | LLM-based JSON classifier | Every message (entry point) |
| **Product Specialist** | Product search, details, comparisons | `search_products`, `get_product_details`, `compare_products` | "What headphones do you have?" |
| **Order Tracker** | Order status, shipping, tracking | `lookup_order`, `get_order_status`, `get_user_orders` | "Where is my order?" |
| **Returns Specialist** | Return eligibility, policy, initiation | `lookup_order`, `check_return_eligibility`, `initiate_return` | "I want to return this item" |
| **Escalation Handler** | Human handoff with conversation summary | None (LLM-only) | "Let me talk to a manager" |

### Routing Flow

1. **User sends message** → Input guardrails validate & sanitize
2. **Router Agent** classifies intent → `product | order | returns | escalation | general`
3. **Confidence check** → If < 0.6, asks for clarification
4. **Specialist agent** runs a ReAct loop: Think → Act (call tool) → Observe → Respond
5. **Output guardrails** validate response (PII redaction, policy compliance)
6. **Response** sent back to frontend with agent badge metadata

### Multi-Turn Memory

Conversations persist across messages using LangGraph's checkpointer system. Each conversation gets a unique `thread_id`, and the full message history is maintained so agents have context from prior turns.

---

## Safety Guardrails

Three layers of protection run on every message:

### 1. Input Validator (`guardrails/input_validator.py`)
- **Prompt injection detection** — 12 regex patterns catching attempts like "ignore previous instructions", "you are now a...", `[system]` tags
- **Message length enforcement** — 2,000 character max
- **HTML stripping** — Removes all HTML tags from input
- **Whitespace normalization** — Collapses excessive whitespace

### 2. Output Validator (`guardrails/output_validator.py`)
- **PII redaction** — Auto-redacts credit card numbers, SSNs, and phone numbers from responses
- **Prohibited content detection** — Catches identity denial, legal advice, false delivery promises, competitor mentions
- **Agent-specific rules** — Returns agent responses are checked for policy compliance

### 3. Policy Engine (`guardrails/policy_engine.py`)
- **Return eligibility enforcement** — Validates order status, return window, product category rules
- **Restocking fee calculation** — Category-based percentage fees
- **VIP member benefits** — Waived restocking fees for VIP-tier customers
- **Refund method determination** — Original payment vs. store credit based on category

---

## Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **Python 3.11+** | Runtime |
| **FastAPI** | REST API framework |
| **LangGraph** | Multi-agent orchestration |
| **LangChain** | LLM abstraction & tool framework |
| **SQLAlchemy** | ORM & database access |
| **SQLite** | Database (file-based, zero-config) |
| **Pydantic** | Request/response validation |
| **SSE-Starlette** | Server-Sent Events for streaming |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Next.js 16** | React framework |
| **React 19** | UI library |
| **TypeScript 5** | Type safety |
| **Tailwind CSS 4** | Styling |
| **Lucide React** | Icons |
| **React Compiler** | Performance optimization |

### LLM Support
| Provider | Models | Mode |
|----------|--------|------|
| **OpenAI** | GPT-4o, GPT-4o-mini, GPT-4-turbo | API key |
| **Anthropic** | Claude Sonnet 4, Claude Haiku 4.5 | API key |

Automatic fallback: Primary model fails → seamlessly switches to fallback model.

---

## Project Structure

```
agentic-customer-care/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory & startup
│   │   ├── config.py                  # Pydantic settings (env-based)
│   │   │
│   │   ├── agents/                    # Multi-agent system
│   │   │   ├── graph.py               # LangGraph StateGraph (wiring)
│   │   │   ├── state.py               # Shared AgentState TypedDict
│   │   │   ├── router_agent.py        # Intent classification
│   │   │   ├── product_agent.py       # Product specialist
│   │   │   ├── order_agent.py         # Order tracking specialist
│   │   │   ├── returns_agent.py       # Returns & refunds specialist
│   │   │   └── escalation_agent.py    # Human handoff agent
│   │   │
│   │   ├── tools/                     # LangChain tools (DB-backed)
│   │   │   ├── product_tools.py       # search, details, compare
│   │   │   ├── order_tools.py         # lookup, status, user orders
│   │   │   ├── returns_tools.py       # eligibility check, initiate
│   │   │   └── user_tools.py          # user lookup
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── product_service.py     # Product queries
│   │   │   ├── order_service.py       # Order queries (with perf logging)
│   │   │   ├── returns_service.py     # Return eligibility & creation
│   │   │   └── user_service.py        # User queries
│   │   │
│   │   ├── guardrails/                # Safety layers
│   │   │   ├── input_validator.py     # Prompt injection, sanitization
│   │   │   ├── output_validator.py    # PII redaction, policy check
│   │   │   └── policy_engine.py       # Return policy enforcement
│   │   │
│   │   ├── llm/                       # LLM provider abstraction
│   │   │   ├── providers.py           # Provider factory (OpenAI, Anthropic)
│   │   │   └── fallback.py            # Primary → fallback chain
│   │   │
│   │   ├── memory/                    # Conversation persistence
│   │   │   ├── checkpointer.py        # LangGraph MemorySaver
│   │   │   └── conversation_store.py  # Thread metadata (in-memory)
│   │   │
│   │   ├── db/                        # Database layer
│   │   │   ├── database.py            # SQLAlchemy engine & session
│   │   │   ├── models.py              # 6 ORM models
│   │   │   ├── seed.py                # Demo data (5 users, 18 orders)
│   │   │   └── seed_bulk.py           # Load test (1K users, 1M orders)
│   │   │
│   │   ├── api/                       # REST API
│   │   │   ├── router.py              # API router assembly
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py            # POST /message, POST /stream
│   │   │   │   ├── conversations.py   # Conversation CRUD
│   │   │   │   └── health.py          # Health check
│   │   │   └── middleware/
│   │   │       ├── cors.py            # CORS setup
│   │   │       └── error_handler.py   # Global error handler
│   │   │
│   │   └── schemas/                   # Pydantic request/response models
│   │       ├── chat.py
│   │       ├── order.py
│   │       ├── product.py
│   │       ├── returns.py
│   │       └── user.py
│   │
│   ├── tests/                         # Test suite
│   ├── requirements.txt               # Python dependencies
│   └── pyproject.toml                 # Project metadata
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx             # Root layout & metadata
│   │   │   ├── page.tsx               # Redirects → /chat
│   │   │   ├── globals.css            # Tailwind + markdown styles
│   │   │   └── chat/
│   │   │       └── page.tsx           # Chat interface page
│   │   │
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx     # Message list + empty state
│   │   │   │   ├── MessageBubble.tsx  # Individual message rendering
│   │   │   │   ├── MessageInput.tsx   # Text input + send button
│   │   │   │   ├── AgentBadge.tsx     # Color-coded agent labels
│   │   │   │   ├── TypingIndicator.tsx# "Agent is thinking..." dots
│   │   │   │   └── MarkdownRenderer.tsx # Zero-dependency MD renderer
│   │   │   └── layout/
│   │   │       ├── Header.tsx         # Top bar + new chat button
│   │   │       └── Sidebar.tsx        # Conversation history
│   │   │
│   │   ├── hooks/
│   │   │   └── useChat.ts            # Chat state management
│   │   │
│   │   └── lib/
│   │       ├── api.ts                # HTTP client (message + stream)
│   │       ├── types.ts              # TypeScript interfaces
│   │       ├── constants.ts          # Agent names, colors, defaults
│   │       └── utils.ts              # cn(), generateId(), timestamps
│   │
│   ├── package.json
│   ├── next.config.ts                # API proxy rewrites
│   └── tsconfig.json
│
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**

### 1. Clone & Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your LLM credentials (see LLM Configuration below)
```

### 2. Seed the Database

```bash
# Standard demo data (5 users, 25 products, 18 orders)
python -m app.db.seed

# OR load test data (1,000 users, 1M orders) — takes ~2 min
python -m app.db.seed_bulk
```

### 3. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Setup & Start Frontend

```bash
cd frontend

npm install
npm run dev
```

### 5. Open the App

Navigate to **http://localhost:3000** — you'll see the chat interface with sample queries to try.

---

## Database & Seed Data

### Schema (6 Tables)

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│  users   │────▶│   orders     │────▶│  order_items   │
│          │     │              │     │                │
│ id       │     │ id           │     │ id             │
│ email    │     │ user_id (FK) │     │ order_id (FK)  │
│ name     │     │ order_number │     │ product_id(FK) │
│ tier     │     │ status       │     │ quantity       │
│          │     │ total_amount │     │ unit_price     │
└──────────┘     │ tracking_num │     └───────┬────────┘
                 │ carrier      │             │
                 └──────┬───────┘             ▼
                        │              ┌──────────────┐
                        ▼              │  products    │
                 ┌──────────────┐      │              │
                 │return_requests│     │ id           │
                 │              │      │ name         │
                 │ order_id(FK) │      │ category     │
                 │ user_id (FK) │      │ price        │
                 │ product_id   │      │ stock        │
                 │ reason       │      │ rating       │
                 │ status       │      └──────────────┘
                 │ refund_amount│
                 └──────────────┘      ┌───────────────┐
                                       │return_policies │
                                       │               │
                                       │ category      │
                                       │ window_days   │
                                       │ restocking_%  │
                                       │ refund_method │
                                       └───────────────┘
```

### Demo Seed (`python -m app.db.seed`)

| Data | Count | Details |
|------|-------|---------|
| Users | 5 | Alice (premium), Bob (standard), Catherine (VIP), David (standard), Emily (premium) |
| Products | 25 | Across 5 categories — electronics, clothing, home & kitchen, sports, books |
| Orders | 18 | Mix of delivered, in_transit, shipped, confirmed, pending, cancelled |
| Return Policies | 5 | One per product category |
| Return Requests | 4 | Approved, denied, requested, completed |

### Bulk Seed (`python -m app.db.seed_bulk`)

| Data | Count | Details |
|------|-------|---------|
| Users | 1,000 | 70% standard, 20% premium, 10% VIP |
| Orders | 1,000,000 | Spread across 6 months with realistic date distribution |
| Order Items | ~1,650,000 | 1-3 items per order |
| DB Size | ~446 MB | SQLite with performance indexes |

**Date distribution for return window testing:**
- 60% historical (30-180 days ago)
- 20% recent (7-30 days ago)
- 15% very recent (1-7 days ago)
- 5% today

**Performance at 1M orders:**
- Single order lookup: < 1ms
- User's orders (~1,000): ~39ms
- Order status check: < 1ms

---

## LLM Configuration

Add at least one API key to `backend/.env`:

### OpenAI (Recommended)

```env
OPENAI_API_KEY=sk-...
PRIMARY_LLM=gpt-4o
FALLBACK_LLM=gpt-4o-mini
```

### Anthropic

```env
ANTHROPIC_API_KEY=sk-ant-...
PRIMARY_LLM=claude-sonnet-4-20250514
FALLBACK_LLM=claude-haiku-4-5-20250514
```

### Both (Best Reliability)

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PRIMARY_LLM=claude-sonnet-4-20250514
FALLBACK_LLM=gpt-4o
```

### Fallback Behavior

The system automatically chains primary → fallback:

```
Request → Primary LLM (GPT-4o)
              │
              ├─ Success → Response
              │
              └─ Failure → Fallback LLM (GPT-4o-mini)
                               │
                               ├─ Success → Response
                               └─ Failure → Error message
```

---

## API Reference

### Chat Endpoints

#### `POST /api/chat/message`

Send a message and receive a complete response.

**Request:**
```json
{
  "message": "Where is my order ORD-2025-00001?",
  "thread_id": null,
  "user_id": 1
}
```

**Response:**
```json
{
  "response": "Your order ORD-2025-00001 is currently in transit...",
  "thread_id": "a1b2c3d4-...",
  "agent": "order",
  "escalated": false,
  "intent": "order"
}
```

#### `POST /api/chat/stream`

Send a message and receive Server-Sent Events.

**Events:**
```
event: metadata
data: {"agent": "order"}

event: token
data: {"token": "Your"}

event: token
data: {"token": " order"}

event: done
data: {"thread_id": "a1b2c3d4-...", "agent": "order"}
```

### Conversation Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/conversations/{user_id}` | List all conversations for a user |
| `GET` | `/api/conversations/{thread_id}/messages` | Get messages for a conversation |
| `DELETE` | `/api/conversations/{thread_id}` | Delete a conversation |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Application health check |

---

## How It Works

### Example: Return Request Flow

**Customer:** "I want to return the Garmin Watch from order ORD-2025-0889745"

```
1. INPUT GUARDRAIL
   ✓ No injection patterns
   ✓ Length OK (< 2000 chars)
   ✓ Sanitized

2. ROUTER AGENT
   LLM classifies: { intent: "returns", confidence: 0.96 }
   → Routes to Returns Specialist

3. RETURNS SPECIALIST (ReAct Loop)

   Think: "Customer wants to return a Garmin Watch. I need the product ID.
           Let me look up the order first."

   Act:   lookup_order("ORD-2025-0889745")

   Observe: "Order ORD-2025-0889745 - Delivered
             Items:
               - Garmin Forerunner 265 (Product ID: 21) | $449.99
               - AirPods Pro (Product ID: 8) | $249.00"

   Think: "Garmin Watch = Product ID 21. Let me check eligibility."

   Act:   check_return_eligibility("ORD-2025-0889745", 21)

   Observe: "ELIGIBLE
             Category: Sports
             Return Window: 45 days (32 remaining)
             Restocking Fee: $0.00 (0%)
             Estimated Refund: $449.99
             Refund Method: Store Credit"

   Respond: "Great news! Your Garmin Forerunner 265 Running Watch
             is eligible for return..."

4. OUTPUT GUARDRAIL
   ✓ No PII detected
   ✓ No prohibited content
   ✓ Returns policy compliant

5. RESPONSE → Frontend with agent="returns"
```

### Example: Product Search Flow

**Customer:** "What laptops do you have under $1500?"

```
Router → intent: "product" (0.95)
  → Product Specialist
    → search_products(query="laptops", max_price=1500)
    → Returns MacBook Air M3 ($1,299.00) with specs
```

### Example: Escalation Flow

**Customer:** "This is unacceptable! I want to speak to a manager NOW!"

```
Router → intent: "escalation" (0.98)
  → Escalation Handler
    → Generates empathetic customer message
    → Creates HANDOFF_SUMMARY for human agent
    → Sets escalation_needed = true
```

---

## Product Catalog

### Electronics (8 products)
| Product | Price | Rating |
|---------|-------|--------|
| Sony WH-1000XM5 Headphones | $349.99 | 4.8/5 |
| MacBook Air M3 | $1,299.00 | 4.9/5 |
| Samsung Galaxy S24 Ultra | $1,199.99 | 4.7/5 |
| LG UltraFine 27" 4K Monitor | $449.99 | 4.6/5 |
| Logitech MX Master 3S Mouse | $99.99 | 4.8/5 |
| Keychron Q1 Pro Mechanical Keyboard | $199.99 | 4.7/5 |
| iPad Pro 13" M4 | $1,299.00 | 4.9/5 |
| AirPods Pro (2nd Gen) | $249.00 | 4.8/5 |

### Clothing (5 products)
| Product | Price | Rating |
|---------|-------|--------|
| Nike Air Zoom Pegasus 41 | $129.99 | 4.5/5 |
| Levi's 501 Original Fit Jeans | $69.50 | 4.4/5 |
| The North Face ThermoBall Jacket | $199.00 | 4.7/5 |
| Essentials Cotton T-Shirt 3-Pack | $29.99 | 4.2/5 |
| Merino Wool Crew Sweater | $89.99 | 4.5/5 |

### Home & Kitchen (5 products)
| Product | Price | Rating |
|---------|-------|--------|
| Instant Pot Duo Plus 6-Quart | $89.99 | 4.7/5 |
| Dyson V15 Detect Vacuum | $749.99 | 4.6/5 |
| Breville Barista Express | $699.95 | 4.5/5 |
| Ninja Foodi 6-in-1 Air Fryer | $179.99 | 4.4/5 |
| Brooklinen Luxe Core Sheet Set | $168.00 | 4.6/5 |

### Sports (4 products)
| Product | Price | Rating |
|---------|-------|--------|
| Manduka PRO Yoga Mat | $120.00 | 4.8/5 |
| Bowflex SelectTech 552 Dumbbells | $429.00 | 4.5/5 |
| Garmin Forerunner 265 | $449.99 | 4.7/5 |
| Wilson Clash 100 v2 Tennis Racket | $249.00 | 4.4/5 |

### Books (3 products)
| Product | Price | Rating |
|---------|-------|--------|
| Python Programming: Beginner to Advanced | $44.99 | 4.6/5 |
| Clean Code | $39.99 | 4.8/5 |
| Atomic Habits | $16.99 | 4.9/5 |

---

## Return Policies

| Category | Return Window | Restocking Fee | Refund Method | Key Conditions | Exceptions |
|----------|:------------:|:--------------:|:-------------:|----------------|------------|
| **Electronics** | 30 days | 15% | Original payment | Original packaging, all accessories included | Opened software, custom-built PCs |
| **Clothing** | 60 days | 0% | Original payment | Tags attached, unworn condition | Swimwear, undergarments |
| **Home & Kitchen** | 30 days | 10% | Original payment | Unused, original packaging | Mattresses after 30-day trial period |
| **Sports** | 45 days | 0% | Store credit | Unused, original packaging | Mouthguards, helmets with impact damage |
| **Books** | 14 days | 0% | Original payment | No writing/highlighting, undamaged | Digital downloads, magazines |

**VIP members** receive waived restocking fees on all categories.

---

## Sample Queries to Try

| Query | Agent | What Happens |
|-------|-------|-------------|
| "What wireless headphones do you have?" | Product Specialist | Searches catalog, shows matching products |
| "Compare the Sony headphones with AirPods Pro" | Product Specialist | Side-by-side feature comparison |
| "Show me my orders" | Order Tracker | Lists all orders for the current user |
| "Where is order ORD-2025-00005?" | Order Tracker | Shows tracking info and delivery estimate |
| "I want to return the headphones from ORD-2025-00001" | Returns Specialist | Looks up order, checks eligibility, shows refund estimate |
| "What's your return policy for electronics?" | Returns Specialist | Explains 30-day window, 15% fee, conditions |
| "I need to speak with a manager" | Escalation Handler | Empathetic response + handoff summary |
| "Hello!" | Router (General) | Friendly greeting, explains capabilities |

---

## Free Deployment Guide

Deploy the entire app for **$0** using Vercel (frontend) + Render (backend).

### Prerequisites

- GitHub account with this repo pushed
- [OpenAI API key](https://platform.openai.com/api-keys) (has free credits for new accounts)
- [Vercel account](https://vercel.com) (free)
- [Render account](https://render.com) (free)

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/agentic-customer-care.git
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   | Setting | Value |
   |---------|-------|
   | **Name** | `agentic-care-backend` |
   | **Root Directory** | `backend` |
   | **Runtime** | Docker |
   | **Instance Type** | Free |

4. Add these **Environment Variables** in the Render dashboard:

   | Key | Value |
   |-----|-------|
   | `LLM_PROVIDER` | `direct` |
   | `OPENAI_API_KEY` | `sk-...` (your actual key) |
   | `PRIMARY_LLM` | `gpt-4o` |
   | `FALLBACK_LLM` | `gpt-4o-mini` |
   | `DATABASE_URL` | `sqlite:///./ecommerce.db` |
   | `ENVIRONMENT` | `production` |
   | `LOG_LEVEL` | `INFO` |
   | `CORS_ORIGINS` | `https://your-app.vercel.app` |

5. Click **Deploy** → Wait for build to complete
6. Copy the URL (e.g., `https://agentic-care-backend.onrender.com`)

> **Note:** The database auto-seeds with demo data on first startup.

### Step 3: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo
3. Configure:
   | Setting | Value |
   |---------|-------|
   | **Framework** | Next.js |
   | **Root Directory** | `frontend` |

4. Add this **Environment Variable**:

   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_API_URL` | `https://agentic-care-backend.onrender.com` |

5. Click **Deploy**

### Step 4: Update CORS

Go back to your Render dashboard and update the `CORS_ORIGINS` env var with your actual Vercel URL:
```
https://agentic-customer-care.vercel.app
```

### That's It!

Your app is now live at your Vercel URL. The architecture:

```
User → Vercel (Next.js frontend)
         │
         │  /api/* proxied via rewrites
         ▼
       Render (FastAPI backend)
         │
         ├── GPT-4o (OpenAI)
         └── SQLite (auto-seeded)
```

### Cost Breakdown

| Service | Plan | Monthly Cost |
|---------|------|:------------:|
| Vercel | Hobby | **$0** |
| Render | Free | **$0** |
| OpenAI GPT-4o | Pay-as-you-go | **~$0.50-2** for light demo use |
| **Total** | | **~$0-2/month** |

> **Tip:** Render free tier spins down after 15 min of inactivity. First request after sleep takes ~30s to cold start. This is normal for free tier.

---

## License

This project is a portfolio demonstration. Built for educational and showcase purposes.
