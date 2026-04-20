# Fabric Workspace Creation — Pipeline Changes

## Summary

Moved Fabric workspace creation from the `azd up` post-provision hook into the scripts pipeline (`02_create_fabric_items.py`), driven by environment variables instead of CLI flags.

## What Changed

### Workspace creation moved to `scripts/02_create_fabric_items.py`
- Auto-creates workspace when `FABRIC_WORKSPACE_ID` is not set but `AZURE_FABRIC_CAPACITY_NAME` is available (set by `azd up`)
- Reuses existing workspace when `FABRIC_WORKSPACE_ID` is already in `.env`
- Writes `FABRIC_WORKSPACE_ID` back to `scripts/.env` after creation

### Workspace cleanup on `azd down`
- Added `predown` hook in `azure.yaml` that runs `scripts/fabric/cleanup_workspace.py`
- Prompts for confirmation before deleting the workspace via Fabric API

### New `scripts/fabric/` folder
- `workspace_setup.py` — Create/reuse workspace and assign to capacity
- `cleanup_workspace.py` — Delete workspace (called by `azd down`)

### Other changes
- `infra/scripts/fabric/fabric_api.py` — Added `delete_workspace()` method
- `scripts/00_build_solution.py` — Removed `--create-workspace` flag; workspace mode auto-detected from env; dynamic step label; UTF-8 encoding fix for Windows subprocess output
- `scripts/02_create_fabric_items.py` — Notebook creation retry handles both `400` and `409` status codes

### Deleted files
- `infra/scripts/fabric/setup_fabric_workspace.py` — Replaced by `scripts/02_create_fabric_items.py`
- `infra/scripts/fabric/helpers/workspace_setup.py` — Moved to `scripts/fabric/workspace_setup.py`

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
