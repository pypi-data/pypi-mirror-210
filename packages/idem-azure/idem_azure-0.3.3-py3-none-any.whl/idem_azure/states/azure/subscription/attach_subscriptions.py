"""State module for managing Attach Subscription."""
import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    management_group_id: str,
    subscription_id: str,
    resource_id: str = None,
) -> Dict:
    r"""Create or update attached subscription to management group.

    Args:
        name(str): The identifier for this state.
        management_group_id(str): management group id to which subscription needs to be associated.
        subscription_id(str): subscription unique id
        resource_id(str, Optional): resource unique id

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            attach_subscription_to_mg_present:
              azure.subscription.attach_subscriptions.present:
                - name: value
                - management_group_id: value
                - subscription_id: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if resource_id is None:
        resource_id = f"/providers/Microsoft.Management/managementGroups/{management_group_id}/subscriptions/{subscription_id}"
    response_get = await hub.exec.azure.subscription.attach_subscriptions.get(
        ctx,
        resource_id=resource_id,
        raw=True,
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
                        "management_group_id": management_group_id,
                        "subscription_id": subscription_id,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.subscription.attach_subscriptions '{name}'"
                )
                return result
            else:
                # PUT operation to attach subscription to management group
                payload = {}
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-05-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not attach subscription to given management group : {response_put['comment']}"
                        f" {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

            result[
                "new_state"
            ] = hub.tool.azure.subscription.subscriptions.convert_raw_attach_subscription_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                management_group_id=management_group_id,
                subscription_id=subscription_id,
                resource_id=resource_id,
            )
            result["comment"].append(
                f"Created azure.subscription.attach_subscriptions '{name}'"
            )
            return result
        else:
            result[
                "old_state"
            ] = hub.tool.azure.subscription.subscriptions.convert_raw_attach_subscription_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                management_group_id=management_group_id,
                subscription_id=subscription_id,
                resource_id=resource_id,
            )
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"No update required azure.subscription.attach_subscriptions '{name}'"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.subscription.attach_subscriptions {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    management_group_id: str,
    subscription_id: str,
) -> Dict:
    r"""De-Associate subscription from management group.

    Args:
        name(str): The identifier for this state.
        management_group_id(str): management group unique id.
        subscription_id(str): subscription unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            detach_subscription_from_mg_absent:
              azure.subscription.attach_subscriptions.absent:
                - name: value
                - management_group_id: value
                - subscription_id: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    resource_id = f"/providers/Microsoft.Management/managementGroups/{management_group_id}/subscriptions/{subscription_id}"
    response_get = await hub.exec.azure.subscription.attach_subscriptions.get(
        ctx,
        resource_id=resource_id,
        raw=True,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.subscription.subscriptions.convert_raw_attach_subscription_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                management_group_id=management_group_id,
                subscription_id=subscription_id,
                resource_id=resource_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would de-associates azure.subscription.attach_subscriptions '{name}'"
                )
                return result

            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-05-01",
                success_codes=[200, 202],
            )

            if not response_delete["result"]:
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"De-associated azure.subscription.attach_subscriptions '{name}'"
            )
            return result
        else:
            # If Azure returns 'Not Found' error, it means the management group is not associated with given subscription.
            result["comment"].append(
                f"azure.subscription.attach_subscriptions '{name}' is not associated with management group"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get subscription attached to management group : '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all subscriptions with respective alias details.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            $ idem describe azure.subscription.attach_subscriptions
    """
    result = {}
    ret_list = await hub.exec.azure.subscription.attach_subscriptions.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe attach subscriptions {ret['comment']}")
        return {}
    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.subscription.attach_subscriptions.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
