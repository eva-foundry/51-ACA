"""
ACA local data model -- FastAPI HTTP server (port 8055).
Exposes the same REST shape as 37-data-model so Veritas works unchanged.
Backed by SQLite via db.py -- persists across restarts.

Start: pwsh -File start.ps1
Docs:  http://localhost:8055/docs
"""
# EVA-STORY: ACA-01-001
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

import db  # sibling module -- data-model/db.py

APP_VERSION = "1.0.0"
PORT = 8055

app = FastAPI(
    title="ACA Data Model",
    description="51-ACA local SQLite-backed data model (EVA-compatible REST API)",
    version=APP_VERSION,
)

# All model layers exposed by this server
ALL_LAYERS = [
    "requirements", "endpoints", "containers", "screens", "agents",
    "services", "personas", "decisions", "schemas", "hooks",
    "components", "literals", "infrastructure", "feature_flags",
    "sprints", "milestones", "wbs",
]


# ---------------------------------------------------------------------------
# Health / ready
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "store": "sqlite",
        "version": APP_VERSION,
        "db_path": str(db.DB_PATH),
        "total_active": db.total_active(),
    }


@app.get("/ready")
def ready():
    ok = db.DB_PATH.exists()
    return {"store_reachable": ok, "status": "ok" if ok else "degraded"}


# ---------------------------------------------------------------------------
# Agent helpers (matching 37-data-model shape)
# ---------------------------------------------------------------------------

@app.get("/model/agent-summary")
def agent_summary():
    counts = db.count_all()
    total = sum(counts.values())
    return {
        "total": total,
        "by_layer": counts,
        "layers": ALL_LAYERS,
    }


@app.get("/model/agent-guide")
def agent_guide():
    return {
        "api": "ACA Data Model v1",
        "base": f"http://localhost:{PORT}",
        "auth": "none (local dev)",
        "layers": ALL_LAYERS,
        "endpoints": {
            "list":   "GET  /model/{layer}/",
            "get":    "GET  /model/{layer}/{id}",
            "upsert": "PUT  /model/{layer}/{id}",
            "create": "POST /model/{layer}/",
            "delete": "DELETE /model/{layer}/{id}",
            "filter_endpoints": "GET /model/endpoints/filter?status=implemented",
        },
        "put_rules": [
            "Always PUT the full object",
            "Strip: layer, modified_by, modified_at, created_by, created_at, row_version, source_file",
            "Include: id, is_active, and all domain fields",
            "Use header X-Actor: agent:your-name",
        ],
    }


# ---------------------------------------------------------------------------
# Model layer CRUD
# ---------------------------------------------------------------------------

@app.get("/model/{layer}/")
def list_objects(layer: str):
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    return db.list_layer(layer)


@app.get("/model/{layer}/{obj_id:path}")
def get_object(layer: str, obj_id: str):
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    obj = db.get_object(layer, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{layer}/{obj_id} not found")
    return obj


@app.put("/model/{layer}/{obj_id:path}")
async def put_object(
    layer: str,
    obj_id: str,
    request: Request,
    x_actor: Optional[str] = Header(default="system", alias="X-Actor"),
):
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    body = await request.json()
    body["id"] = obj_id  # enforce id from URL path
    try:
        stored = db.upsert_object(layer, body, actor=x_actor or "system")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return stored


@app.post("/model/{layer}/")
async def create_object(
    layer: str,
    request: Request,
    x_actor: Optional[str] = Header(default="system", alias="X-Actor"),
):
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    body = await request.json()
    if not body.get("id"):
        raise HTTPException(status_code=422, detail="Body must contain 'id' field")
    try:
        stored = db.upsert_object(layer, body, actor=x_actor or "system")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return stored


@app.delete("/model/{layer}/{obj_id:path}")
def delete_object(
    layer: str,
    obj_id: str,
    x_actor: Optional[str] = Header(default="system", alias="X-Actor"),
):
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    deleted = db.delete_object(layer, obj_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"{layer}/{obj_id} not found")
    return {"status": "deleted", "layer": layer, "id": obj_id}


# ---------------------------------------------------------------------------
# Endpoint filter (special route matching 37-data-model)
# ---------------------------------------------------------------------------

@app.get("/model/endpoints/filter")
def filter_endpoints(status: Optional[str] = None):
    items = db.list_layer("endpoints")
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


# ---------------------------------------------------------------------------
# Impact / graph (stub -- returns empty for now)
# ---------------------------------------------------------------------------

@app.get("/model/impact/")
def impact(container: Optional[str] = None):
    """Return endpoints that read/write the named container."""
    eps = db.list_layer("endpoints")
    if container:
        eps = [
            e for e in eps
            if container in (e.get("cosmos_reads") or [])
            or container in (e.get("cosmos_writes") or [])
        ]
    return eps


@app.get("/model/graph/")
def graph(node_id: Optional[str] = None, depth: int = 2):
    """Stub -- returns node + direct neighbours."""
    result = {"node_id": node_id, "depth": depth, "nodes": [], "edges": []}
    return result


# ---------------------------------------------------------------------------
# Admin (wipe / commit / validate)
# ---------------------------------------------------------------------------

@app.post("/model/admin/wipe/{layer}")
def wipe_layer(layer: str, authorization: Optional[str] = Header(default=None)):
    if authorization != "Bearer dev-admin":
        raise HTTPException(status_code=401, detail="Authorization required")
    if layer not in ALL_LAYERS:
        raise HTTPException(status_code=404, detail=f"Unknown layer: {layer}")
    count = db.wipe_layer(layer)
    return {"status": "wiped", "layer": layer, "deleted": count}


@app.post("/model/admin/commit")
def commit(authorization: Optional[str] = Header(default=None)):
    """No-op validate+export cycle for local dev. Always passes."""
    counts = db.count_all()
    total = sum(counts.values())
    return {
        "status": "PASS",
        "violation_count": 0,
        "exported_total": total,
        "export_errors": [],
        "by_layer": counts,
        "note": "SQLite-backed -- no external export needed",
    }


@app.post("/model/admin/validate")
def validate(authorization: Optional[str] = Header(default=None)):
    return {"count": 0, "violations": [], "status": "PASS"}


@app.post("/model/admin/export")
def export(authorization: Optional[str] = Header(default=None)):
    counts = db.count_all()
    return {"status": "PASS", "exported": sum(counts.values())}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)
