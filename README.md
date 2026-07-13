# 🐨 Koala

Academic Roadmap, Notes & Progress Tracker — an AI-assisted study companion.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) Docker for local Postgres

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head          # run migrations
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd web
npm install
npm run dev                   # starts at http://localhost:5173
```

### Environment
Copy `.env.example` to `.env` and fill in your Supabase credentials.

## Architecture
- **Auth**: Supabase Auth (Google OAuth + email/password)
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage (file uploads)
- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **Billing**: LemonSqueezy (Pro tier)

## Project Structure
```
├── backend/          # FastAPI API server
├── web/              # React + Vite frontend
├── test/             # UI prototype (static HTML)
├── docs/             # SRS and documentation
└── docker-compose.yml
```
