#!/usr/bin/env python3
"""
Cleanup Fabric Workspace

Deletes the Fabric workspace created during provisioning.
Called automatically by `azd down` via the predown hook.

Reads FABRIC_WORKSPACE_ID from:
  1. Environment variable (set by azd)
  2. scripts/.env file
"""

import os
import sys

# Add infra fabric path for FabricApiClient
_infra_fabric_dir = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "infra", "scripts", "fabric")
)
sys.path.insert(0, _infra_fabric_dir)

from fabric_api import FabricApiClient, FabricApiError, create_fabric_client


def main() -> None:
    """Delete Fabric workspace if one was created."""

    # Try environment variable first, then scripts/.env
    workspace_id = os.getenv("FABRIC_WORKSPACE_ID", "").strip()

    if not workspace_id:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
        env_path = os.path.normpath(env_path)
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("FABRIC_WORKSPACE_ID"):
                        workspace_id = line.split("=", 1)[1].strip().strip("'\"")
                        break

    if not workspace_id:
        print("No FABRIC_WORKSPACE_ID found. Skipping workspace cleanup.")
        return

    print(f"\nFabric Workspace Cleanup")
    print("=" * 60)
    print(f"Workspace ID: {workspace_id}")

    try:
        fabric_client = create_fabric_client()

        # Verify the workspace exists before deleting
        url = f"{FabricApiClient.BASE_URL}/workspaces/{workspace_id}"
        import requests

        token = fabric_client._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        resp = requests.get(url, headers=headers)

        if resp.status_code == 404:
            print(f"Workspace {workspace_id} not found (already deleted).")
            return

        if resp.status_code == 200:
            ws_name = resp.json().get("displayName", "Unknown")
            print(f"Workspace:    {ws_name}")

            confirm = input(
                f"\nDelete workspace '{ws_name}' ({workspace_id})? [y/N]: "
            ).strip().lower()
            if confirm != "y":
                print("Skipped workspace deletion.")
                return

            fabric_client.delete_workspace(workspace_id)
            print(f"[OK] Workspace '{ws_name}' deleted successfully.")
        else:
            print(f"[WARN] Could not verify workspace: {resp.status_code}")
            print("Skipping deletion to be safe.")

    except FabricApiError as exc:
        print(f"[WARN] Failed to delete workspace: {exc}")
        print("You can delete it manually from https://app.fabric.microsoft.com")
    except Exception as exc:
        print(f"[WARN] Unexpected error: {exc}")
        print("You can delete it manually from https://app.fabric.microsoft.com")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user")
        sys.exit(1)
