# Data Model Split Analysis
**Date**: 2026-03-05  
**Discovery**: Port 8055 (local) and Port 8010 (central) have different content

---

## Current State

### Port 8055 (51-ACA Local SQLite)
```
✅ 370 objects loaded
├── 281 stories (ACA-01-001 through ACA-15-017)
├── 15 epics (ACA-01 through ACA-15)
├── endpoints (ACA-specific)
├── services (ACA-specific)
├── containers (Cosmos schema)
├── agents (ACA analysis agents)
└── infrastructure (Bicep, IaC specific to ACA)
```

**Source**: `seed-from-plan.py --reseed-model` executed ✅ earlier in session

### Port 8010 (Central 37-data-model Cosmos)
```
✅ 4,315 objects loaded
├── 48 other projects (01-documentation-generator, 02-poc-agent-skills, ..., 50-eva-ops)
├── Project metadata for 51-ACA (NAME, PHASE, MTI, story_count) ← JUST REGISTERED
├── BUT: NO ACA-NN-NNN stories
├── BUT: NO ACA-specific endpoints/services/agents
└── Reason: Central model has other project's historical data, not 51-ACA's current stories
```

---

## Problem Statement

**Governance Documentation** says:
> "Central EVA data model (port 8010) is single source of truth for all project entities"

**Reality**:
- ✅ Project metadata is in central (port 8010)
- ❌ Project stories are in local (port 8055)
- ❌ Not unified

---

## Design Decision Required

### Option A: Keep Current Split (Project-specific isolation)
**Architecture**:
- Port 8010 (Cosmos) - Project metadata + cross-project relationships only
- Port 8055 (SQLite) - 51-ACA detailed stories, owned by project
- **Justification**: Lighter central model, projects own their data
- **Trade-off**: Cannot query "all stories across all projects" from one place

### Option B: Push ACA Stories to Central (Unified)
**Architecture**:
- Port 8010 (Cosmos) - Complete project catalog including all 281 ACA stories
- Port 8055 (SQLite) - DEPRECATED, no longer used
- **Justification**: Single source of truth, workspace-wide visibility
- **Trade-off**: Central model becomes much larger (4315 + 281 + other projects)

### Option C: Hybrid (Central owns master, local is cache)
**Architecture**:
- Port 8010 (Cosmos) - Master copy of all stories for all projects
- Port 8055 (SQLite) - Cached read-only copy of ACA data (syncs from central)
- **Justification**: Fast local queries, but central is source of truth
- **Trade-off**: Need sync mechanism (cron job or push-on-write)

---

## Governance Files State

What we **documented**:
> "Central 37-data-model on port 8010 is the exclusive source of truth"

What is **actually true**:
- Metadata: ✅ Central (8010)
- Stories: ❌ Local (8055)

**Alignment Issue**: Docs claim unified, reality is split.

---

## Recommendation

Given the context from copilot-instructions.md and project 37's design:

**Use Option A + clarify in docs** because:
1. Project 37 design already supports per-project models
2. ACA has historical local SQLite setup with 281 stories already loaded
3. Central model has lighter footprint (easier to manage)
4. Cross-project queries still work (use central for metadata, aggregate locally if needed)

**Action**: Update governance docs to clarify the split:
- Port 8010: Project metadata + shared infrastructure  
- Port 8055: ACA story details (owned by project)
- Both are "source of truth" for their respective domains

---

## Files Affected

Current alignment docs assume unified model:
- `copilot-instructions.md` -- Says central is "exclusive source of truth" (needs clarification)
- `README.md` -- References central model (needs split clarification)  
- `PLAN.md` -- References central model (needs split clarification)

---

## Required Clarifications

Update all three documents to state:
```
Data Model Split (by design):
  
  Port 8010 (Central):
    - Project metadata (name, phase, maturity, MTI score, story count)
    - Cross-project relationships and impact analysis
    - Shared infrastructure (personas, services, containers, endpoints - WORKSPACE-WIDE)
    
  Port 8055 (Local to 51-ACA):
    - ACA project stories (281 ACA-NN-NNN)
    - ACA-specific agents, screens, services
    - ACA Cosmos schema definitions
    - Source of truth for ACA implementation details
```

This is a **design choice**, not a bug.
