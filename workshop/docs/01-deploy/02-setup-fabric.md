# Fabric Setup

Create and configure your Microsoft Fabric workspace for Fabric IQ.

!!! note "Using Azure-Only Mode?"
    If you set `AZURE_ENV_ONLY=true` before running `azd up`, you can **skip this page** and proceed directly to [Configure dev environment](03-configure.md).

!!! tip "Automated Fabric Setup (Recommended)"
    When running in **workshop mode** (default), Fabric Capacity is **automatically created** during `azd up`. The Fabric Workspace is created later by the build script (step 02) when `CREATE_FABRIC_WORKSPACE` is enabled.

    - To **auto-create a workspace**, set the flag before running the build script:
      ```bash
      azd env set CREATE_FABRIC_WORKSPACE true
      ```
    - To use an **existing Fabric capacity**, set the env var before running `azd up`:
      ```bash
      azd env set EXISTING_FABRIC_CAPACITY_NAME "your-capacity-name"
      ```
    - To use an **existing Fabric workspace**, set:
      ```bash
      azd env set FABRIC_WORKSPACE_ID "your-workspace-id"
      ```
    - To change the **capacity SKU** (default: F2):
      ```bash
      azd env set FABRIC_CAPACITY_SKU "F8"
      ```

    If automated setup succeeds, you can skip the manual steps below and go directly to [Step 3](#step-3-verify-workspace-settings).

## Prerequisites

- An active Azure subscription with permissions to create resources
- Workspace admin permissions

---

## Step 1 — Create a Fabric capacity in Azure

!!! tip "Already have a Fabric capacity?"
    If you already have a Fabric capacity (F8+), you can **skip this step** and use your existing capacity. Proceed to [Step 2](#step-2-create-a-fabric-workspace).

If you need to create a new Fabric capacity, follow the instructions here:
**[Create a Fabric capacity in Azure →](02a-create-fabric-capacity.md)**

---

## Step 2 — Create a Fabric workspace

!!! tip "Already have a Fabric workspace?"
    If you already have a Fabric workspace linked to a Fabric capacity, you can **skip this step** and use your existing workspace. Proceed to [Step 3](#step-3-verify-workspace-settings).

If you need to create a new Fabric workspace, follow the instructions here:
**[Create a Fabric workspace →](02b-create-fabric-workspace.md)**

---

## Step 3 — Verify workspace settings

!!! warning "Fabric IQ must be enabled"
    Ensure that [Fabric IQ is enabled on your tenant](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview-tenant-settings) before proceeding.

1. Open your newly created workspace or an existing workspace.

2. Click the **Workspace settings** gear icon (⚙️) in the top-right area.

    ![Open workspace settings](../assets/fabric/13-workspace-settings.png)

3. Go to **Workspace type** and verify:

    - [x] The workspace is assigned to a **Fabric capacity**
    - [x] The capacity SKU is **F8** or higher

    ![Verify Workspace type](../assets/fabric/14-license-info.png)

---

## Step 4 — Retrieve the workspace ID

You will need the workspace ID to configure the solution in the next step.

1. Open your workspace in the browser.

2. Look at the URL — the workspace ID is the GUID that appears after `/groups/`:

    ```
    https://app.fabric.microsoft.com/groups/{workspace-id}/...
    ```

    ![Copy workspace ID from URL](../assets/fabric/15-workspace-id.png)

3. Copy the workspace ID and save it for later. You'll use it in the [Configure dev environment](03-configure.md) step.

!!! tip "Finding the workspace ID"
    For more details, refer to the Microsoft documentation: [Identify your workspace ID](https://learn.microsoft.com/en-us/fabric/admin/portal-workspace#identify-your-workspace-id).

---

## Summary

You should now have:

| Item |
|------|
| Fabric capacity created in Azure (F8+) |
| Fabric workspace created and linked to capacity |
| Workspace ID copied for configuration |

!!! success "Ready to Continue"
    You have your Fabric workspace ready. Proceed to configure your dev environment.

---

[← Deploy Azure resources](01-deploy-azure.md) | [Configure dev environment →](03-configure.md)
