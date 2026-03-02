"""
ACA local data model -- SQLite backend.
Single table: objects(layer, id, data JSON, is_active, row_version, modified_by, modified_at).
Primary key: (layer, id).
No external dependencies -- stdlib sqlite3 only.
"""
# EVA-STORY: ACA-12-001
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).parent / "aca-model.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS objects (
    layer       TEXT NOT NULL,
    id          TEXT NOT NULL,
    data        TEXT NOT NULL DEFAULT '{}',
    is_active   INTEGER NOT NULL DEFAULT 1,
    row_version INTEGER NOT NULL DEFAULT 1,
    modified_by TEXT NOT NULL DEFAULT 'system',
    modified_at TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (layer, id)
);
CREATE INDEX IF NOT EXISTS idx_objects_layer ON objects(layer);
CREATE INDEX IF NOT EXISTS idx_objects_active ON objects(layer, is_active);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create schema if not present."""
    with _connect() as conn:
        conn.executescript(SCHEMA)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Merge stored JSON fields with metadata columns."""
    data = json.loads(row["data"])
    data["id"] = row["id"]
    data["layer"] = row["layer"]
    data["is_active"] = bool(row["is_active"])
    data["row_version"] = row["row_version"]
    data["modified_by"] = row["modified_by"]
    data["modified_at"] = row["modified_at"]
    data["created_at"] = row["created_at"]
    return data


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def list_layer(layer: str, active_only: bool = False) -> list[dict]:
    """Return all objects in a layer."""
    with _connect() as conn:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM objects WHERE layer=? AND is_active=1 ORDER BY id",
                (layer,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM objects WHERE layer=? ORDER BY id",
                (layer,),
            ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_object(layer: str, obj_id: str) -> Optional[dict]:
    """Return one object or None."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM objects WHERE layer=? AND id=?",
            (layer, obj_id),
        ).fetchone()
    return _row_to_dict(row) if row else None


def upsert_object(
    layer: str,
    obj: dict,
    actor: str = "system",
) -> dict:
    """
    INSERT or UPDATE.  Strips internal metadata from obj before storing
    so data column holds only domain fields.
    Returns the stored object with updated metadata.
    """
    obj_id = obj.get("id", "")
    if not obj_id:
        raise ValueError(f"Object missing 'id' field: {obj}")

    # Strip audit/meta fields -- store only domain data
    SKIP = {"id", "layer", "row_version", "modified_by", "modified_at",
            "created_at", "source_file"}
    domain = {k: v for k, v in obj.items() if k not in SKIP}
    is_active = int(domain.pop("is_active", True))
    data_json = json.dumps(domain, ensure_ascii=True)
    now = _now()

    with _connect() as conn:
        existing = conn.execute(
            "SELECT row_version, created_at FROM objects WHERE layer=? AND id=?",
            (layer, obj_id),
        ).fetchone()

        if existing:
            rv = existing["row_version"] + 1
            created_at = existing["created_at"]
            conn.execute(
                """UPDATE objects SET data=?, is_active=?, row_version=?,
                           modified_by=?, modified_at=?
                   WHERE layer=? AND id=?""",
                (data_json, is_active, rv, actor, now, layer, obj_id),
            )
        else:
            rv = 1
            created_at = now
            conn.execute(
                """INSERT INTO objects(layer, id, data, is_active, row_version,
                           modified_by, modified_at, created_at)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (layer, obj_id, data_json, is_active, rv, actor, now, now),
            )

    stored = domain.copy()
    stored["id"] = obj_id
    stored["layer"] = layer
    stored["is_active"] = bool(is_active)
    stored["row_version"] = rv
    stored["modified_by"] = actor
    stored["modified_at"] = now
    stored["created_at"] = created_at
    return stored


def deactivate_layer(layer: str, actor: str = "system") -> int:
    """Mark every object in a layer inactive. Returns count updated."""
    now = _now()
    with _connect() as conn:
        cur = conn.execute(
            """UPDATE objects SET is_active=0, modified_by=?, modified_at=?,
                      row_version=row_version+1
               WHERE layer=? AND is_active=1""",
            (actor, now, layer),
        )
    return cur.rowcount


def delete_object(layer: str, obj_id: str) -> bool:
    """Hard-delete one object. Returns True if deleted."""
    with _connect() as conn:
        cur = conn.execute(
            "DELETE FROM objects WHERE layer=? AND id=?",
            (layer, obj_id),
        )
    return cur.rowcount > 0


def wipe_layer(layer: str) -> int:
    """Hard-delete all objects in a layer. Returns count deleted."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM objects WHERE layer=?", (layer,))
    return cur.rowcount


def count_all() -> dict[str, int]:
    """Return {layer: count} for all layers with active objects."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT layer, COUNT(*) as cnt FROM objects WHERE is_active=1 GROUP BY layer"
        ).fetchall()
    return {r["layer"]: r["cnt"] for r in rows}


def total_active() -> int:
    with _connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM objects WHERE is_active=1"
        ).fetchone()
    return row["cnt"] if row else 0


# ---------------------------------------------------------------------------
# Evidence seeding
# ---------------------------------------------------------------------------

def seed_evidence(repo_root: Optional[Path] = None, actor: str = "seed:evidence") -> dict:
    """
    Import all evidence receipt files from .eva/evidence/ into the evidence layer.
    Returns {imported: int, skipped: int, errors: list}.
    """
    if repo_root is None:
        repo_root = Path(__file__).parent.parent  # 51-ACA root
    evidence_dir = repo_root / ".eva" / "evidence"
    
    if not evidence_dir.exists():
        return {"imported": 0, "skipped": 0, "errors": ["Evidence dir does not exist"]}
    
    imported = 0
    skipped = 0
    errors = []
    
    for receipt_file in evidence_dir.glob("*-receipt.json"):
        try:
            with open(receipt_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # story_id is the primary key
            story_id = data.get("story_id")
            if not story_id:
                errors.append(f"{receipt_file.name}: missing story_id")
                skipped += 1
                continue
            
            # Upsert into evidence layer
            data["id"] = story_id
            upsert_object("evidence", data, actor=actor)
            imported += 1
            
        except json.JSONDecodeError as e:
            errors.append(f"{receipt_file.name}: JSON decode error: {e}")
            skipped += 1
        except Exception as e:
            errors.append(f"{receipt_file.name}: {e}")
            skipped += 1
    
    return {"imported": imported, "skipped": skipped, "errors": errors}


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
init_db()

if __name__ == "__main__":
    print(f"[INFO] ACA data model DB: {DB_PATH}")
    print(f"[INFO] Total active objects: {total_active()}")
    for layer, cnt in sorted(count_all().items()):
        print(f"  {layer}: {cnt}")
