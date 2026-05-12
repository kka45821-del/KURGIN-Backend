# FastAPI Skeleton

This is a minimal scaffold for the KURGIN backend contract.
It is not production-ready until database, password hashing, token rotation,
CORS, payments, and audit logging are fully implemented.

Run locally:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

```txt
http://localhost:8000/docs
```
