# Fabric Workspace Management

## Overview

Fabric workspace lifecycle (creation, reuse, cleanup) is managed inline in `scripts/02_create_fabric_items.py` and `scripts/00_build_solution.py`, driven by environment variables. The workspace ID is persisted to both `scripts/.env` and the azd environment (`.azure/<env>/.env`) to keep them in sync.

## Workspace Creation

When `FABRIC_WORKSPACE_ID` is not set, the pipeline auto-creates a workspace using the Fabric capacity provisioned by `azd up`. The flow:

1. `00_build_solution.py` checks for a workspace ID via CLI arg, env var, or interactive prompt
2. If none is found but `AZURE_FABRIC_CAPACITY_NAME` exists, `02_create_fabric_items.py` auto-creates a workspace
3. The new workspace ID is saved to:
   - `scripts/.env` (for project-level persistence)
   - azd env via `azd env set` (so `.azure/<env>/.env` stays in sync)
   - Current process environment (for downstream steps)

Workspace helper functions (create, assign to capacity, lookup by name) are defined inline in `02_create_fabric_items.py`.

## Workspace Reuse

When `FABRIC_WORKSPACE_ID` is already set, the pipeline skips creation and reuses the existing workspace. The workspace is also matched by name — if a workspace with the expected name already exists in Fabric, it is reused even if the ID wasn't persisted locally.

## Workspace Cleanup

Running `azd down` triggers the predown hook: `python scripts/02_create_fabric_items.py --cleanup`

This:
1. Looks up the workspace by ID
2. Prompts for confirmation before deletion
3. Deletes the workspace via Fabric API
4. Clears `FABRIC_WORKSPACE_ID` from both `scripts/.env` and azd env

## Environment Variable Sync

`FABRIC_WORKSPACE_ID` is persisted to two locations to avoid state drift:

| Location | Purpose |
|---|---|
| `scripts/.env` | Project-level settings, loaded by `load_env.py` |
| `.azure/<env>/.env` | azd environment, loaded first by `load_azd_env()` |

Both files are updated on workspace creation, user input, and cleanup. This ensures `load_all_env()` always picks up the correct value regardless of load order.

## Behavior Matrix

| `FABRIC_WORKSPACE_ID` | `AZURE_FABRIC_CAPACITY_NAME` | Behavior |
|---|---|---|
| Set | (any) | Reuses existing workspace |
| Empty | Set | Auto-creates workspace |
| Empty | Empty | Prompts user for workspace ID |

## Usage

```bash
# Fresh deployment — auto-creates workspace
azd up
python scripts/00_build_solution.py

# Rerun — reuses workspace from .env
python scripts/00_build_solution.py

# Custom data
python scripts/00_build_solution.py --custom-data data/customdata

# Tear down (deletes workspace + Azure resources)
azd down
```
