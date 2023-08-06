"""State module for managing Resource Group."""
import copy
from typing import Any
from typing import Dict


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    location: str,
    subscription_id: str = None,
    resource_id: str = None,
    tags: Dict = None,
) -> dict:
    r"""Create or update Resource Groups.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group to create or update. Can include alphanumeric, underscore, parentheses, hyphen, period (except at end), and Unicode characters that match the allowed characters.Regex pattern: ^[-\w\._\(\)]+$.
        location(str): Resource location.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Resource Group id on Azure.
        tags(dict, Optional): Resource tags.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.resource_management.resource_groups.present:
                - name: value
                - resource_group_name: value
                - subscription_id: value
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
        resource_id = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        )
    response_get = await hub.exec.azure.resource_management.resource_groups.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"] is None:
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "subscription_id": subscription_id,
                        "tags": tags,
                        "location": location,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.resource_management.resource_groups '{name}'"
                )
                return result

            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.resource_management.resource_groups.convert_present_to_raw_resource_group(
                    location=location,
                    tags=tags,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                    success_codes=[200, 201],
                    json=payload,
                )

                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create Resource Groups {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

            result[
                "new_state"
            ] = hub.tool.azure.resource_management.resource_groups.convert_raw_resource_group_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(
                f"Created azure.resource_management.resource_groups '{name}'"
            )
            return result
        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.resource_management.resource_groups.convert_raw_resource_group_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.resource_management.resource_groups.update_resource_groups_payload(
                existing_resource,
                {"tags": tags},
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.resource_management.resource_groups '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.resource_management.resource_groups.convert_raw_resource_group_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.resource_management.resource_groups '{name}'"
                    )
                return result
            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.resource_management.resource_groups '{name}' has no property need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                success_codes=[200, 201],
                json=new_payload["ret"],
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.resource_management.resource_groups {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.resource_management.resource_groups.convert_raw_resource_group_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(
                f"Updated azure.resource_management.resource_groups '{name}'"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.resource_management.resource_groups {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub, ctx, name: str, resource_group_name: str, subscription_id: str = None
) -> dict:
    r"""Delete Resource Groups.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group to delete. The name is case insensitive.Regex pattern: ^[-\w\._\(\)]+$.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.resource_management.resource_groups.absent:
                - name: value
                - resource_group_name: value
                - subscription_id: value
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
    )
    response_get = await hub.exec.azure.resource_management.resource_groups.get(
        ctx, resource_id=resource_id
    )
    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.resource_management.resource_groups '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                success_codes=[200, 202],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.resource_management.resource_groups {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.resource_management.resource_groups '{name}'"
            )
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.resource_management.resource_groups '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.resource_management.resource_groups '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Resource Groups under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.resource_management.resource_groups
    """
    result = {}
    ret_list = await hub.exec.azure.resource_management.resource_groups.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe resource_groups {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.resource_management.resource_groups.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
