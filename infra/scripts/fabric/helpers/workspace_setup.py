"""
Fabric Workspace Setup Module

Creates or retrieves a Fabric workspace and assigns it to a capacity.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fabric_api import FabricApiClient, FabricApiError


def setup_workspace(
    fabric_client: FabricApiClient, capacity_name: str, workspace_name: str
) -> str:
    """
    Create or retrieve a Fabric workspace and assign it to a capacity.

    Args:
        fabric_client: Authenticated Fabric API client
        capacity_name: Name of the capacity to assign
        workspace_name: Name of the workspace to create

    Returns:
        str: Workspace ID
    """
    print(f"🏢 Setting up workspace: {workspace_name}")

    # Look up capacity
    print(f"   Looking up capacity: {capacity_name}")
    capacity = fabric_client.get_capacity(capacity_name)
    if not capacity:
        raise FabricApiError(f"Capacity '{capacity_name}' not found")

    capacity_id = capacity["id"]
    print(f"   ✅ Found capacity: {capacity_name} ({capacity_id})")

    # Check for existing workspace
    print(f"   Checking if workspace '{workspace_name}' exists...")
    workspace = fabric_client.get_workspace(workspace_name)

    if workspace:
        workspace_id = workspace["id"]
        print(f"   ℹ️  Workspace already exists: {workspace_name} ({workspace_id})")

        current_capacity_id = workspace.get("capacityId")
        if current_capacity_id == capacity_id:
            print(f"   ✅ Workspace already assigned to capacity: {capacity_name}")
        else:
            print(f"   🔄 Assigning workspace to capacity: {capacity_name}")
            try:
                fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
                print(f"   ✅ Successfully assigned workspace to capacity")
            except FabricApiError as e:
                # Verify actual state on failure
                refreshed = fabric_client.get_workspace(workspace_name)
                if refreshed and refreshed.get("capacityId") == capacity_id:
                    print(
                        f"   ⚠️  Assignment call failed but workspace is on correct capacity. Continuing..."
                    )
                else:
                    raise
    else:
        # Create new workspace
        print(f"   Creating new workspace: {workspace_name}")
        workspace_id = fabric_client.create_workspace(workspace_name)
        print(f"   ✅ Created workspace: {workspace_name} ({workspace_id})")

        # Assign to capacity
        print(f"   🔄 Assigning workspace to capacity: {capacity_name}")
        fabric_client.assign_workspace_to_capacity(workspace_id, capacity_id)
        print(f"   ✅ Successfully assigned workspace to capacity")

    return workspace_id
