# ContentOps AI ⚡ — Grounded Multi-Channel Content Engine

[![Nuxt 3](https://img.shields.io/badge/Frontend-Nuxt%203-00DC82?logo=nuxt.js)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20RLS-3ECF8E?logo=supabase)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)

> **ContentOps AI** is an intelligent content engine that transforms long-form whitepapers, articles, transcripts, and PDFs into coordinated, fact-checked 7-day multi-channel social campaigns.

---

## 🌟 Key Features

- 📄 **Source Document Ingestion**: Upload PDF, Markdown, or paste raw text. Full verbatim context indexing up to 10MB.
- 🧬 **Content DNA Extraction**: Automatically extracts core thesis statements, brand tone, target audience personas, key verified claims, and quote references.
- 🗓️ **7-Day Multi-Platform Campaigns**: Generates structured post schedules for **LinkedIn**, **X (Twitter)**, **Threads**, and **Instagram**.
- 🔍 **Source-Grounded QA Auditor**: Runs automated quote matching & claim verification. Generates color-coded scores for *Faithfulness*, *Source Coverage*, and *Brand Fit*.
- 📦 **Multi-Format Export**: Export full campaigns as **Markdown (`.md`)**, **JSON**, or **CSV**.
- 🔐 **Supabase RLS Security**: Row-Level Security ensures all source materials and campaign assets remain private per user account.

---

## 🛠️ Architecture & Tech Stack

```
contentops/
├── backend/          # FastAPI REST API (Python 3.11)
│   ├── app/
│   │   ├── ai/       # Generation, Content DNA & QA Audit engine
│   │   ├── api/      # FastAPI endpoints & security dependencies
│   │   ├── db/       # Repositories & Supabase client integration
│   │   └── services/ # Domain business logic & exporters
│   └── tests/        # 19 automated unit tests
├── frontend/         # Nuxt 3 Vue Web Application
│   ├── components/   # Asset Cards, QA Reports, Calendar views
│   ├── composables/  # Custom API & Supabase Auth composables
│   ├── pages/        # Dashboard, Source Ingest, Campaign Matrix
│   └── assets/css/   # Tailwind CSS + Custom Dark Mode Styles
└── supabase/
    └── migrations/   # SQL schema migrations & RLS policies
```

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+
- Supabase project account (or Supabase CLI)

### 1. Repository Clone
```bash
git clone https://github.com/saintsmile001/contentops.git
cd contentops
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install

# Copy environment variables
cp .env.example .env

# Run Nuxt dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser to start creating campaigns!

---

## 🧪 Running Unit Tests

To run the backend test suite:

```bash
cd backend
python -m unittest discover -s tests -v
```

---

## 🔒 Security & Environment Configuration

Make sure your `.env` files contain your Supabase credentials:

**`backend/.env`**:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
APP_ENV=development
```

**`frontend/.env`**:
```env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NUXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

---

