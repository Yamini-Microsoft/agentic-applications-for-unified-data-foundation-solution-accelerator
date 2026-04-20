# Fabric Workspace Creation — Pipeline Changes

## Summary

Fabric workspace creation and cleanup are handled inline in `scripts/02_create_fabric_items.py`, driven by environment variables. No separate scripts or subfolders.

## What Changed

### Workspace creation in `scripts/02_create_fabric_items.py`
- Auto-creates workspace when `FABRIC_WORKSPACE_ID` is not set but `AZURE_FABRIC_CAPACITY_NAME` is available (set by `azd up`)
- Reuses existing workspace when `FABRIC_WORKSPACE_ID` is already in `.env`
- Writes `FABRIC_WORKSPACE_ID` back to `scripts/.env` after creation
- Workspace helper functions (create, assign to capacity, lookup) are inline — no separate modules

### Workspace cleanup via `--cleanup` flag
- `azure.yaml` predown hook runs `python scripts/02_create_fabric_items.py --cleanup`
- Prompts for confirmation before deleting the workspace via Fabric API
- Clears `FABRIC_WORKSPACE_ID` from `scripts/.env` after successful deletion

## How It Works

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
