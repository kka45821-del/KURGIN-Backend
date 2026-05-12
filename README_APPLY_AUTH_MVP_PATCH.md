# Apply KURGIN Backend Auth MVP V1 Patch

Upload the contents of this archive to `kka45821-del/KURGIN-Backend`, preserving paths.

Required paths:

```txt
fastapi_skeleton/.env.example
fastapi_skeleton/requirements.txt
fastapi_skeleton/requirements-dev.txt
fastapi_skeleton/app/config.py
fastapi_skeleton/app/db.py
fastapi_skeleton/app/models.py
fastapi_skeleton/app/access_policy.py
fastapi_skeleton/app/security.py
fastapi_skeleton/app/main.py
fastapi_skeleton/app/routes/auth.py
fastapi_skeleton/app/routes/access.py
fastapi_skeleton/app/routes/plans.py
fastapi_skeleton/app/routes/payments.py
fastapi_skeleton/app/routes/workspace.py
fastapi_skeleton/app/routes/score.py
fastapi_skeleton/app/routes/admin.py
fastapi_skeleton/tools/local_smoke_test.py
fastapi_skeleton/README_AUTH_MVP.md
Final Report.txt
```

Commit message:

```txt
Implement backend auth MVP V1
```

After upload, run locally from `fastapi_skeleton`:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python tools/local_smoke_test.py
uvicorn app.main:app --reload
```
