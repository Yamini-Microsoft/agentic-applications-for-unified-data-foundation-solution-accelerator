"""
Microsoft Fabric API Client

Simplified client for workspace and capacity operations via Fabric REST APIs.
Adapted from the unified-data-foundation-with-fabric-solution-accelerator.
"""

import json
import time
from typing import Optional

from azure.identity import DefaultAzureCredential


class FabricApiError(Exception):
    """Custom exception for Fabric API errors."""
    pass


class FabricApiClient:
    """Client for Microsoft Fabric REST API operations."""

    BASE_URL = "https://api.fabric.microsoft.com/v1"
    SCOPE = "https://api.fabric.microsoft.com/.default"

    def __init__(self, credential=None):
        self.credential = credential or DefaultAzureCredential()
        self._token = None

    def _get_token(self) -> str:
        """Get or refresh the access token."""
        self._token = self.credential.get_token(self.SCOPE).token
        return self._token

    def _headers(self) -> dict:
        """Build request headers with authorization."""
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, **kwargs) -> dict:
        """Make an HTTP request with error handling."""
        import requests

        response = requests.request(method, url, headers=self._headers(), **kwargs)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 30))
            print(f"   ⏳ Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
            response = requests.request(method, url, headers=self._headers(), **kwargs)

        if response.status_code >= 400:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text
            raise FabricApiError(
                f"HTTP {response.status_code} {method} {url}: {error_detail}"
            )

        if response.status_code == 204 or not response.text:
            return {}

        return response.json()

    # ---- Capacity Operations ----

    def list_capacities(self) -> list:
        """List all accessible Fabric capacities."""
        url = f"{self.BASE_URL}/capacities"
        result = self._request("GET", url)
        return result.get("value", [])

    def get_capacity(self, capacity_name: str) -> Optional[dict]:
        """Get a capacity by name (case-insensitive)."""
        capacities = self.list_capacities()
        for cap in capacities:
            if cap.get("displayName", "").lower() == capacity_name.lower():
                return cap
        return None

    # ---- Workspace Operations ----

    def list_workspaces(self) -> list:
        """List all accessible workspaces."""
        url = f"{self.BASE_URL}/workspaces"
        result = self._request("GET", url)
        return result.get("value", [])

    def get_workspace(self, workspace_name: str) -> Optional[dict]:
        """Get a workspace by name (case-insensitive)."""
        workspaces = self.list_workspaces()
        for ws in workspaces:
            if ws.get("displayName", "").lower() == workspace_name.lower():
                return ws
        return None

    def create_workspace(self, workspace_name: str) -> str:
        """Create a new Fabric workspace. Returns workspace ID."""
        url = f"{self.BASE_URL}/workspaces"
        body = {"displayName": workspace_name}
        result = self._request("POST", url, json=body)
        workspace_id = result.get("id")
        if not workspace_id:
            raise FabricApiError(f"Workspace creation returned no ID: {result}")
        return workspace_id

    def assign_workspace_to_capacity(self, workspace_id: str, capacity_id: str) -> None:
        """Assign a workspace to a Fabric capacity."""
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/assignToCapacity"
        body = {"capacityId": capacity_id}
        self._request("POST", url, json=body)

    def add_workspace_role_assignment(
        self, workspace_id: str, principal_id: str, principal_type: str, role: str = "Admin"
    ) -> None:
        """Add a role assignment to a workspace."""
        url = f"{self.BASE_URL}/workspaces/{workspace_id}/roleAssignments"
        body = {
            "principal": {"id": principal_id, "type": principal_type},
            "role": role,
        }
        self._request("POST", url, json=body)


def create_fabric_client() -> FabricApiClient:
    """Create an authenticated Fabric API client using DefaultAzureCredential."""
    return FabricApiClient()
