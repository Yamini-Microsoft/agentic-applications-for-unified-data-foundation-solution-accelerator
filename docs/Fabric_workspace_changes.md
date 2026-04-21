# Fabric Workspace Management

## Overview

Fabric workspace lifecycle (creation, reuse, cleanup) is managed inline in `scripts/02_create_fabric_items.py` and `scripts/00_build_solution.py`, driven by the `CREATE_FABRIC_WORKSPACE` environment flag. The workspace ID is persisted to both `scripts/.env` and the azd environment (`.azure/<env>/.env`) to keep them in sync.

## Workspace Creation

Workspace creation is controlled by the `CREATE_FABRIC_WORKSPACE` flag (default: `false`).

To enable workspace auto-creation:

```bash
azd env set CREATE_FABRIC_WORKSPACE true
```

When `CREATE_FABRIC_WORKSPACE` is `true`, the flow is:

1. `00_build_solution.py` detects the flag and delegates to `02_create_fabric_items.py`
2. `02_create_fabric_items.py` looks up `AZURE_FABRIC_CAPACITY_NAME` and creates a workspace (or reuses one with the same name)
3. The new workspace ID is saved to:
   - `scripts/.env` (for project-level persistence)
   - azd env via `azd env set` (so `.azure/<env>/.env` stays in sync)
   - Current process environment (for downstream steps)

When `CREATE_FABRIC_WORKSPACE` is `false` (default), users must set `FABRIC_WORKSPACE_ID` directly:

```bash
azd env set FABRIC_WORKSPACE_ID "your-workspace-id"
```

Workspace helper functions (create, assign to capacity, lookup by name) are defined inline in `02_create_fabric_items.py`.

## Workspace Reuse

When `CREATE_FABRIC_WORKSPACE` is `true` and a workspace with the expected name already exists in Fabric, it is reused rather than creating a duplicate.

## Workspace Cleanup

Running `azd down` triggers the predown hook, but only when `CREATE_FABRIC_WORKSPACE` is `true` (since the workspace was auto-created and should be auto-cleaned):

```
python scripts/02_create_fabric_items.py --cleanup
```

This:
1. Looks up the workspace by ID
2. Prompts for confirmation before deletion (use `--yes` to skip prompt)
3. Deletes the workspace via Fabric API
4. Clears `FABRIC_WORKSPACE_ID` from both `scripts/.env` and azd env

The `--yes`/`-y` flag skips the confirmation prompt for non-interactive environments (CI pipelines, `azd down`).

## Environment Variable Sync

`FABRIC_WORKSPACE_ID` is persisted to two locations to avoid state drift:

| Location | Purpose |
|---|---|
| `scripts/.env` | Project-level settings, loaded by `load_env.py` |
| `.azure/<env>/.env` | azd environment, loaded first by `load_azd_env()` |

Both files are updated on workspace creation, user input, and cleanup. This ensures `load_all_env()` always picks up the correct value regardless of load order.

## Behavior Matrix

| `CREATE_FABRIC_WORKSPACE` | Behavior |
|---|---|
| `true` | Auto-creates workspace using `AZURE_FABRIC_CAPACITY_NAME` (or reuses by name) |
| `false` (default) | Uses `FABRIC_WORKSPACE_ID` directly (errors if not set) |

## Related Parameters

| Parameter | Description |
|---|---|
| `CREATE_FABRIC_WORKSPACE` | Set to `true` to auto-create a Fabric workspace (default: `false`) |
| `AZURE_FABRIC_CAPACITY_NAME` | Name of the Fabric capacity (provisioned by `azd up`) |
| `FABRIC_WORKSPACE_ID` | Workspace ID — set manually when `CREATE_FABRIC_WORKSPACE` is `false` |
| `FABRIC_ADMIN_MEMBERS` | Array of object IDs for Fabric Capacity Admin role (e.g. `'["id1","id2"]'`) |

## Usage

```bash
# Option A: Auto-create workspace
azd env set CREATE_FABRIC_WORKSPACE true
azd up
python scripts/00_build_solution.py

# Option B: Use existing workspace
azd env set FABRIC_WORKSPACE_ID "your-workspace-id"
azd up
python scripts/00_build_solution.py

# Rerun — reuses workspace from .env
python scripts/00_build_solution.py

# Custom data
python scripts/00_build_solution.py --custom-data data/customdata

# Tear down (deletes workspace if auto-created + Azure resources)
azd down
```
