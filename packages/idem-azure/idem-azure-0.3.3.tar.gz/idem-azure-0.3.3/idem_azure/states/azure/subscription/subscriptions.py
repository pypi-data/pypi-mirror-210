"""State module for managing Subscription."""
import copy
from typing import Any
from typing import Dict

__contracts__ = ["resource"]
__reconcile_wait__ = {"static": {"wait_in_seconds": 20}}


async def present(
    hub,
    ctx,
    name: str,
    alias: str,
    billing_scope: str,
    display_name: str,
    workload: str,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Subscription.

    Args:
        name(str): The identifier for this state.
        alias(str): The alias name of the subscription to create or update. Can include alphanumeric,
          underscore, parentheses, hyphen, period (except at end), and Unicode characters that match
          the allowed characters.Regex pattern: ^[-\w\._\(\)]+$.
        billing_scope(str): billing scope associated with billing account id and enrollment account id to create subscription
        display_name(str): subscription display name
        workload(str): type of workload where subscription needs to be created. Can be Production/DevTest
        resource_id(str, Optional): resource unique id

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_present:
              azure.subscription.subscriptions.present:
                - name: create_subscription_3
                - alias: dupSubTest
                - billing_scope: /providers/Microsoft.Billing/billingAccounts/{billingAccountID}/enrollmentAccounts/{enrollmentAccountId}}
                - display_name: Subscription Display Name
                - workload: Production
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if resource_id is None:
        resource_id = f"/providers/Microsoft.Subscription/aliases/{alias}"
    response_get = await hub.exec.azure.subscription.subscriptions.get(
        ctx, resource_id=resource_id, raw=True
    )
    hub.log.debug(f"Get Subscription details : {response_get}")

    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.subscriptions.subscription '{name}' {response_get['comment']} {response_get['ret']}"
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
                    "alias": alias,
                    "display_name": display_name,
                    "subscription_id": "subscription_id_known_after_present",
                    "resource_id": resource_id,
                },
            )
            result["comment"].append(
                f"Would create azure.subscription.subscriptions '{name}'"
            )
            return result
        else:
            # PUT operation to create subscription
            payload = hub.tool.azure.subscription.subscriptions.convert_present_to_raw_subscription(
                billing_scope=billing_scope,
                display_name=display_name,
                workload=workload,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-09-01",
                success_codes=[200, 201],
                json=payload,
            )
            if not response_put["result"]:
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

        result[
            "new_state"
        ] = hub.tool.azure.subscription.subscriptions.convert_raw_subscription_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            alias=alias,
            display_name=display_name,
            subscription_id=None,
            resource_id=resource_id,
        )
        result["comment"].append(f"Created azure.subscription.subscriptions '{name}'")
        return result

    else:
        # Update/rename subscription display name if given subscription already present
        # and display name is modified in the input
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.subscription.subscriptions.convert_raw_subscription_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            alias=alias,
            display_name=None,
            subscription_id=None,
            resource_id=resource_id,
        )
        subscription_id = result["old_state"]["subscription_id"]
        # Generate a new PUT operation payload with new values
        is_display_name_updated = display_name != existing_resource.get("displayName")
        if ctx.get("test", False):
            if not is_display_name_updated:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.subscription.subscriptions '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.subscription.subscriptions.convert_raw_subscription_to_present(
                    resource=response_get["ret"],
                    idem_resource_name=name,
                    alias=alias,
                    display_name=display_name,
                    subscription_id=None,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Would update azure.subscription.subscriptions '{name}'"
                )
            return result
        # POST operation to rename subscription display_name
        if not is_display_name_updated:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.subscription.subscriptions '{name}' has no property need to be updated."
            )
            return result
        rename_payload = {"subscriptionName": display_name}
        response_rename = await hub.exec.request.json.post(
            ctx,
            url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Subscription/rename?api-version=2020-09-01",
            success_codes=[200, 201],
            json=rename_payload,
        )
        if not response_rename["result"]:
            hub.log.debug(
                f"Could not update azure.subscription.subscriptions {response_rename['comment']} {response_rename['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_rename["comment"], response_rename["ret"]]
            return result

        result["new_state"] = copy.deepcopy(result["old_state"])
        result["new_state"]["display_name"] = display_name
        result["comment"].append(f"Updated azure.subscription.subscriptions '{name}'")
        return result


async def absent(hub, ctx, name: str, alias: str) -> Dict:
    r"""Delete Subscription. This state disables the subscription and deletes respective alias.

    Once subscription is in disabled state, after 90 days it gets deleted automatically.

    Args:
        name(str): The identifier for this state.
        alias(str): The alias name of the subscription to delete.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            subscription_is_absent:
              azure.subscription.subscriptions.absent:
                - name: value
                - alias: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    resource_id = f"/providers/Microsoft.Subscription/aliases/{alias}"
    response_get = await hub.exec.azure.subscription.subscriptions.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.subscriptions.subscription '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name
        subscription_id = response_get["ret"]["subscription_id"]
        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.subscription.subscriptions '{name}'"
            )
            return result

        # Cancel the subscription before deleting
        # Once subscription is cancelled, it will be in disabled state and after 90 days it gets deleted automatically.
        response_cancel = await hub.exec.request.json.post(
            ctx,
            url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Subscription/cancel?api-version=2020-09-01",
            success_codes=[200, 202],
        )
        if not response_cancel["result"]:
            result["result"] = False
            result["comment"] = [response_cancel["comment"], response_cancel["ret"]]
            return result

        # Delete subscription alias.
        # After deleting the subscription with alias, deleted alias can be used to create new subscription
        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-09-01",
            success_codes=[200, 202],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.subscription.subscriptions {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(f"Deleted azure.subscription.subscriptions '{name}'")
        return result
    else:
        # If Azure returns 'Not Found' error, it means the management group is not associated with given subscription.
        result["comment"].append(
            f"azure.subscriptions.subscription '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe subscriptions in a way that can be recreated/managed with the corresponding "present" function.

    Lists all subscriptions.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            $ idem describe azure.subscription.subscriptions
    """
    result = {}
    ret_list = await hub.exec.azure.subscription.subscriptions.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe subscription subscriptions {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.subscription.subscriptions.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
