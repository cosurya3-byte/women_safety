# Sahaaya — Smart Women Security Application

Full-stack academic project covering the first ten specified functional modules only. External actions are explicitly simulated; no real SMS/calls, police/CCTV data, background recording, biometric authentication, or cloud storage is claimed.

## Start locally

```bash
cd women-security-system
docker compose up -d postgres
cp backend/.env.example backend/.env
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
# Optional, once migrations are generated: alembic revision --autogenerate -m "initial schema" && alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd women-security-system/frontend
cp .env.example .env
npm install
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`). Register an account and use OTP `123456` only while `DEV_OTP_MODE=true`.

## Database and API

The configured PostgreSQL URL is in `backend/.env`. API docs: `http://localhost:8000/docs`. The application creates the initial local schema at startup for a frictionless first run; use Alembic revisions for all schema evolution.

## Testing

```bash
cd backend
pytest
```

## Important limitations

The browser may deny camera, microphone or location permissions. Fake calls, notifications and contact messages are in-app simulations. The threat engine is transparent, rule-based, and designed to be exchanged for a future ML implementation.
