from fastapi import APIRouter, Depends

from ..security import require_admin

router = APIRouter()


@router.get("/audit")
def audit_log(user: dict = Depends(require_admin)):
    # TODO: Query admin_audit_logs.
    return []
