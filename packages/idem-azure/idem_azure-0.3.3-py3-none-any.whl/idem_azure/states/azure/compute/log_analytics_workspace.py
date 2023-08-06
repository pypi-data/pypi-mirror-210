"""State module for managing Compute Log Analytics Workspace."""
import copy
from collections import OrderedDict
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    subscription_id: str,
    workspace_name: str,
    location: str,
    eTag: str = None,
    default_data_collection_rule_resourceId: str = None,
    features: Dict = None,
    force_cmk_for_query: bool = False,
    public_network_access_for_ingestion: str = None,
    public_network_access_for_query: str = None,
    retention_in_days: int = None,
    sku: Dict = None,
    workspace_capping: Dict = None,
    tags: Dict = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Log Analytics Workspace.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group. The name is case insensitive.
        workspace_name(str): The name of the workspace. Regex pattern: ^[A-Za-z0-9][A-Za-z0-9-]+[A-Za-z0-9]$
        eTag(str): The ETag of the workspace.
        location(str): Resource location. This field can not be updated.
        resource_id(str, Optional): Workspace resource id on Azure
        default_data_collection_rule_resourceId(str): The resource ID of the default Data Collection Rule to use for this workspace.
        features(dict, Optional): Workspace features.
        force_cmk_for_query(dict, Optional): Indicates whether customer managed storage is mandatory for query management.
        public_network_access_for_ingestion(str, Optional): The network access type for accessing Log Analytics ingestion.
        public_network_access_for_query(str, Optional): The network access type for accessing Log Analytics query.
        retention_in_days(int, Optional): The workspace data retention in days. Allowed values are per pricing plan. See pricing tiers documentation for details.
        sku(dict, Optional): The SKU of the workspace.
        workspace_capping(dict): The daily volume cap for ingestion.
        tags(dict, Optional): Resource tags.
        subscription_id(str): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            workspaces/sb-instance:
             azure.compute.log_analytics_workspace.present:
              - name: /subscriptions/98bf10bb-cf16-49eb-9ef3-7ccc82e5d45e/resourcegroups/sb-resource-group/providers/Microsoft.OperationalInsights/workspaces/sb-workspace
              - resource_id: /subscriptions/98bf10bb-cf16-49eb-9ef3-7ccc82e5d45e/resourcegroups/sb-resource-group/providers/Microsoft.OperationalInsights/workspaces/sb-workspace
              - resource_group_name: sb-resource-group
              - workspace_name: sb-workspace
              - location: westus
              - subscription_id: 98bf10bb-cf16-49eb-9ef3-7ccc82e5d45e
              - tags:
                  E2ETag: E2EValue
                  Environment: Next
                  env: next
              - sku:
                  lastSkuUpdate: '2022-12-13T05:51:07.1724412Z'
                  name: pergb2018
              - features:
                  enableLogAccessUsingOnlyResourcePermissions: true
                  legacy: 0
                  searchVersion: 1
              - workspace_capping:
                  dailyQuotaGb: -1.0
                  dataIngestionStatus: RespectQuota
                  quotaNextResetTime: '2022-12-13T08:00:00Z'
              - retention_in_days: 30
              - public_network_access_for_ingestion: Enabled
              - public_network_access_for_query: Enabled
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    if resource_id is None:
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"
    response_get = await hub.exec.azure.compute.log_analytics_workspace.get(
        ctx, resource_id=resource_id, raw=True
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.compute.log_analytics_workspace {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if not response_get["ret"]:
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_group_name": resource_group_name,
                    "subscription_id": subscription_id,
                    "workspace_name": workspace_name,
                    "location": location,
                    "eTag": eTag,
                    "default_data_collection_rule_resourceId": default_data_collection_rule_resourceId,
                    "features": features,
                    "force_cmk_for_query": force_cmk_for_query,
                    "public_network_access_for_ingestion": public_network_access_for_ingestion,
                    "public_network_access_for_query": public_network_access_for_query,
                    "retention_in_days": retention_in_days,
                    "sku": sku,
                    "workspace_capping": workspace_capping,
                    "tags": tags,
                    "resource_id": resource_id,
                },
            )
            result["comment"].append(
                f"Would create azure.compute.log_analytics_workspace '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.compute.log_analytics_workspace.convert_present_log_analytics_workspace_to_raw(
                subscription_id=subscription_id,
                public_network_access_for_query=public_network_access_for_query,
                public_network_access_for_ingestion=public_network_access_for_ingestion,
                retention_in_days=retention_in_days,
                workspace_capping=workspace_capping,
                features=features,
                sku=sku,
                location=location,
                tags=tags,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{hub.exec.azure.URL}{resource_id}?api-version=2021-12-01-preview",
                success_codes=[200, 201],
                json=payload,
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.compute.log_analytics {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.compute.log_analytics_workspace.convert_raw_log_analytics_workspace_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                workspace_name=workspace_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(
                f"Created azure.compute.log_analytics_workspace '{name}'"
            )
            return result

    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.compute.log_analytics_workspace.convert_raw_log_analytics_workspace_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        # Generate a new PUT operation payload with new values
        new_payload = hub.tool.azure.compute.log_analytics_workspace.update_log_analytics_workspace_payload(
            subscription_id,
            response_get["ret"],
            {
                "retention_in_days": retention_in_days,
                "public_network_access_for_ingestion": public_network_access_for_ingestion,
                "public_network_access_for_query": public_network_access_for_query,
                "tags": tags,
                "features": features,
                "sku": sku,
                "workspace_capping": workspace_capping,
            },
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.compute.log_analytics_workspace '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.compute.log_analytics_workspace.convert_raw_log_analytics_workspace_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    workspace_name=workspace_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Would update azure.compute.log_analytics_workspace '{name}'"
                )
            return result
        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.compute.log_analytics_workspace '{name}' has no property need to be updated."
            )
            return result
        result["comment"] += new_payload["comment"]
        response_put = await hub.exec.request.json.put(
            ctx,
            url=f"{hub.exec.azure.URL}{resource_id}?api-version=2021-12-01-preview",
            success_codes=[200],
            json=new_payload["ret"],
        )

        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.compute.log_analytics_workspace {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_put["comment"], response_put["ret"]]
            return result

        result[
            "new_state"
        ] = hub.tool.azure.compute.log_analytics_workspace.convert_raw_log_analytics_workspace_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        result["comment"].append(
            f"Updated azure.compute.log_analytics_workspace '{name}'"
        )
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    workspace_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete a Log Analytics Workspace.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        workspace_name(str): The name of the workspace.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.compute.log_analytics_workspace.absent:
                - name: my-workspace
                - resource_group_name: my-resource-group
                - workspace_name: my-workspace
                - subscription_id: my-subscription
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}"
    )
    response_get = await hub.exec.azure.compute.log_analytics_workspace.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.compute.log_analytics_workspace '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name
        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.compute.log_analytics_workspace '{name}'"
            )
            return result

        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{hub.exec.azure.URL}{resource_id}?api-version=2021-12-01-preview",
            success_codes=[200, 202, 204],
        )
        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.compute.log_analytics_workspace {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(
            f"Deleted azure.compute.log_analytics_workspace '{name}'"
        )
        return result
    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.compute.log_analytics_workspace '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Log Analytics Workspace under the same subscription


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.compute.log_analytics_workspace
    """
    result = {}
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "resourcegroups": "resource_group_name",
            "workspaces": "workspace_name",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{hub.exec.azure.URL}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.OperationalInsights/workspaces?api-version=2021-12-01-preview",
        success_codes=[200],
    ):
        resource_list = page_result.get("value", None)
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                resource_translated = hub.tool.azure.compute.log_analytics_workspace.convert_raw_log_analytics_workspace_to_present(
                    resource=resource,
                    idem_resource_name=resource_id,
                    subscription_id=subscription_id,
                    resource_id=resource_id,
                    **uri_parameter_values,
                )
                result[resource_id] = {
                    f"azure.compute.log_analytics_workspace.present": [
                        {parameter_key: parameter_value}
                        for parameter_key, parameter_value in resource_translated.items()
                    ]
                }
    return result
