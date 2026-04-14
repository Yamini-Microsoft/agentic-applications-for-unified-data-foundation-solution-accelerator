#!/usr/bin/env python3
"""
Setup Fabric Workspace for Agentic Apps Workshop

This script automates Fabric Workspace creation and capacity assignment
as a post-provision step when running in workshop mode.

It is called automatically by `azd up` when IS_WORKSHOP=true and
AZURE_ENV_ONLY is not true.

Environment Variables (set automatically by azd from main.bicep outputs):
    AZURE_FABRIC_CAPACITY_NAME           (required) Name of the Fabric capacity.
    SOLUTION_SUFFIX                      (required) Suffix for resource naming.
    AZURE_FABRIC_CAPACITY_ADMINISTRATORS (required) JSON array of capacity admin identities.
    EXISTING_FABRIC_WORKSPACE_ID         (optional) If set, skip workspace creation.
    FABRIC_WORKSPACE_NAME                (optional) Override default workspace name.
"""

import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from fabric_api import FabricApiError, create_fabric_client
from helpers.workspace_setup import setup_workspace


SOLUTION_NAME = "Agentic Apps UDF"


def get_required_env_var(var_name: str) -> str:
    """Get a required environment variable or exit."""
    value = os.getenv(var_name)
    if not value:
        print(f"❌ Error: Required environment variable '{var_name}' is not set")
        sys.exit(1)
    return value


def main() -> None:
    """Set up Fabric workspace for the Agentic Apps workshop."""

    # Check if we should skip (existing workspace provided)
    existing_workspace_id = os.getenv("EXISTING_FABRIC_WORKSPACE_ID", "").strip()
    if existing_workspace_id:
        print(f"ℹ️  Using existing Fabric workspace: {existing_workspace_id}")
        print(f"   Skipping workspace creation.")
        return

    # Get required environment variables
    capacity_name = get_required_env_var("AZURE_FABRIC_CAPACITY_NAME")
    solution_suffix = get_required_env_var("SOLUTION_SUFFIX")
    workspace_name = os.getenv(
        "FABRIC_WORKSPACE_NAME", f"{SOLUTION_NAME} - {solution_suffix}"
    )

    # Startup banner
    print(f"\n🏭 {SOLUTION_NAME} – Fabric Workspace Setup")
    print("=" * 60)
    print(f"Capacity:        {capacity_name}")
    print(f"Workspace:       {workspace_name}")
    print(f"Solution Suffix: {solution_suffix}")
    print(f"Start time:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Authenticate
    print("\n🔐 Authenticating Fabric API client...")
    try:
        fabric_client = create_fabric_client()
        print("   ✅ Fabric API client authenticated")
    except Exception as exc:
        print(f"   ❌ Failed to authenticate: {exc}")
        sys.exit(1)

    # Create/setup workspace
    try:
        workspace_id = setup_workspace(
            fabric_client=fabric_client,
            capacity_name=capacity_name,
            workspace_name=workspace_name,
        )
    except FabricApiError as exc:
        print(f"\n❌ Fabric API Error: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌ Unexpected error: {exc}")
        sys.exit(1)

    # Success
    workspace_url = f"https://app.fabric.microsoft.com/groups/{workspace_id}"
    print(f"\n{'='*60}")
    print(f"🎉 FABRIC WORKSPACE SETUP COMPLETE!")
    print(f"{'='*60}")
    print(f"📅 Completed:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"☁️  Workspace:  {workspace_name}")
    print(f"🔗 Workspace ID: {workspace_id}")
    print(f"🌐 URL:        {workspace_url}")
    print(f"{'='*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
