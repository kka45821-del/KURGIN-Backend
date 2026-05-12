from __future__ import annotations

from typing import Any, Dict, Tuple


def evaluate_access(user: Dict[str, Any], resource: str) -> Tuple[bool, str]:
    """Evaluate role/plan access for MVP.

    This is a backend-side policy function. Website, Analyzer, Workspace and
    Admin must not duplicate authorization rules in public frontend code.
    """

    roles = set(user.get("roles", []))
    plan = str(user.get("plan") or "free")
    normalized = resource.strip().lower()

    if normalized in {"public", "public_diamonds", "academy", "information"}:
        return True, "public_resource"

    if normalized in {"single_report", "score_single"}:
        if plan in {"single_report", "pro", "partner"} or roles & {"admin", "support"}:
            return True, "paid_plan"
        return False, "paid_plan_required"

    if normalized in {"professional_analytics", "excel_batch", "workspace"}:
        if plan in {"pro", "partner"} or roles & {"jeweler", "designer", "gemologist", "partner", "admin"}:
            return True, "professional_access"
        return False, "professional_access_required"

    if normalized.startswith("admin") or normalized == "admin":
        if "admin" in roles:
            return True, "admin_role"
        return False, "admin_role_required"

    if normalized in {"partner_pricing", "b2b_price"}:
        if plan == "partner" or roles & {"partner", "admin"}:
            return True, "partner_access"
        return False, "partner_access_required"

    return False, "unknown_resource"
