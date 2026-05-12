from __future__ import annotations

from fastapi import APIRouter, Depends

from ..db import list_audit_logs
from ..security import require_admin

router = APIRouter()


@router.get("/audit")
def audit_log(user: dict = Depends(require_admin)):
    return list_audit_logs()
