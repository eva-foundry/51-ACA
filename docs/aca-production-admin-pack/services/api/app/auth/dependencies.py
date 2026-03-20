from fastapi import Header
from app.auth.rbac import Actor

# Production integration point:
# Replace this stub with:
# - Entra JWT signature validation
# - app role / group extraction
# - oid/sub extraction for actor_id
#
# Temporary debug headers:
#   X-Debug-ActorId
#   X-Debug-Roles
#   X-Debug-DisplayName

def get_actor(
    x_debug_actorid: str = Header(default="debug-operator", alias="X-Debug-ActorId"),
    x_debug_roles: str = Header(default="ACA_Admin", alias="X-Debug-Roles"),
    x_debug_displayname: str = Header(default="Debug Operator", alias="X-Debug-DisplayName"),
) -> Actor:
    roles = {r.strip() for r in x_debug_roles.split(",") if r.strip()}
    return Actor(actor_id=x_debug_actorid, roles=roles, display_name=x_debug_displayname)
