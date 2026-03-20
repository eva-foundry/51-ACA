from dataclasses import dataclass
from typing import Iterable, Set
from fastapi import HTTPException, status

@dataclass(frozen=True)
class Actor:
    actor_id: str
    roles: Set[str]
    display_name: str | None = None

ROLE_ADMIN = "ACA_Admin"
ROLE_SUPPORT = "ACA_Support"
ROLE_FINOPS = "ACA_FinOps"

def require_any_role(actor: Actor, allowed: Iterable[str]) -> None:
    allowed_set = set(allowed)
    if not actor.roles.intersection(allowed_set):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Missing required role",
                    "allowed": sorted(list(allowed_set)),
                }
            },
        )

def require_admin(actor: Actor) -> None:
    require_any_role(actor, [ROLE_ADMIN])

def require_support_or_admin(actor: Actor) -> None:
    require_any_role(actor, [ROLE_ADMIN, ROLE_SUPPORT])

def require_finops_or_admin(actor: Actor) -> None:
    require_any_role(actor, [ROLE_ADMIN, ROLE_FINOPS])
