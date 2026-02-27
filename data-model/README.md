ACA Data Model
==============

51-ACA owns this data model completely. No dependency on 37-data-model.
Store: SQLite (`aca-model.db`, persists across restarts, gitignored).
Port: 8055 (local dev server).

=============================================================================
DUAL PURPOSE
=============================================================================

This data model serves TWO purposes:

1. BUILD-TIME: Source of truth for the WBS, epics, features, and user stories
   that drive the ACA development process. Every story in PLAN.md is seeded
   here. Agents read and update story status as work progresses.

2. RUNTIME: Source of truth for the ACA app itself at runtime -- feature
   flags, enabled/disabled analysis rules, endpoint metadata, Cosmos container
   schema, service health, and agent configuration.

=============================================================================
STORAGE
=============================================================================

SQLite database: data-model/aca-model.db (persists across restarts).
Gitignored -- rebuilt from PLAN.md on demand.

Layers stored: requirements, endpoints, containers, screens, agents, services,
               personas, decisions, schemas, hooks, components, literals,
               infrastructure, feature_flags, sprints, milestones, wbs

=============================================================================
START THE HTTP SERVER
=============================================================================

  pwsh -File C:\AICOE\eva-foundry\51-ACA\data-model\start.ps1
  # http://localhost:8055
  # Swagger: http://localhost:8055/docs

=============================================================================
REBUILD FROM PLAN.MD
=============================================================================

  cd C:\AICOE\eva-foundry\51-ACA
  C:\AICOE\.venv\Scripts\python.exe scripts/seed-from-plan.py --reseed-model

  # Dry-run (no writes):
  C:\AICOE\.venv\Scripts\python.exe scripts/seed-from-plan.py --dry-run

=============================================================================
DIRECT SQLITE QUERY (no server needed)
=============================================================================

  python -c "import sys; sys.path.insert(0,'data-model'); import db; print(db.total_active(), db.count_all())"

=============================================================================
HTTP QUICK REFERENCE (port 8055)
=============================================================================

  $b = "http://localhost:8055"

  # Health and summary
  Invoke-RestMethod "$b/health"
  Invoke-RestMethod "$b/model/agent-summary"

  # Endpoint discovery
  Invoke-RestMethod "$b/model/endpoints/filter?status=implemented"
  Invoke-RestMethod "$b/model/endpoints/filter?status=stub"

  # WBS progress
  Invoke-RestMethod "$b/model/requirements/" | Where-Object { $_.status -eq "done" } | Measure-Object

  # Commit (validate, always PASS for local SQLite)
  Invoke-RestMethod "$b/model/admin/commit" -Method POST -Headers @{"Authorization"="Bearer dev-admin"}

=============================================================================
VERITAS
=============================================================================

  node C:\AICOE\eva-foundry\48-eva-veritas\src\cli.js audit --repo C:\AICOE\eva-foundry\51-ACA
  # Target MTI >= 70 before Phase 1 go-live

