"""Exec module for managing Attach Subscriptions"""

__func_alias__ = {"list_": "list"}

from typing import Dict
from collections import OrderedDict


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict:
    """Gets the subscription attached to a management group from azure account.

    Args:
        resource_id(str):
            The resource id of the subscription attached to a management group.
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.subscription.attach_subscriptions.get resource_id="/providers/Microsoft.Management/managementGroups/{management_group_id}/subscriptions/{subscription_id}" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.subscription.attach_subscriptions.get
                - kwargs:
                    resource_id: /providers/Microsoft.Management/managementGroups/{management_group_id}/subscriptions/{subscription_id}
                    raw: False
    """

    result = dict(comment=[], ret=None, result=True)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-05-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result
    uri_parameters = OrderedDict({"managementGroups": "management_group_id"})
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        response_get["ret"]["properties"]["parent"]["id"], uri_parameters
    )
    if raw:
        result["ret"] = response_get["ret"]
    else:
        result[
            "ret"
        ] = hub.tool.azure.subscription.subscriptions.convert_raw_attach_subscription_to_present(
            resource=response_get["ret"],
            idem_resource_name=resource_id,
            resource_id=resource_id,
            subscription_id=response_get["ret"]["name"],
            **uri_parameter_values,
        )

    return result


async def list_(
    hub,
    ctx,
) -> Dict:
    """Lists all Attached Subscriptions.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.subscription.attach_subscriptions.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.subscription.attach_subscriptions.list

    """

    result = dict(comment=[], ret=[], result=True)

    uri_parameters = OrderedDict({"managementGroups": "management_group_id"})
    ret = await hub.exec.request.json.post(
        ctx,
        url=f"{ctx.acct.endpoint_url}/providers/Microsoft.Management/getEntities?api-version=2020-05-01&$view=SubscriptionsOnly",
        success_codes=[200],
    )
    if not ret["result"]:
        hub.log.debug("Could not describe attach_subscription")
    resource_list = ret["ret"].get("value", None)
    if resource_list:
        for resource in resource_list:
            subscription_id = resource["name"]
            uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                resource["properties"]["parent"]["id"], uri_parameters
            )
            resource_id = f"/providers/MicrosoftManagement/managementGroups/{uri_parameter_values.get('management_group_id')}/subscriptions/{subscription_id}"
            result["ret"].append(
                hub.tool.azure.subscription.subscriptions.convert_raw_attach_subscription_to_present(
                    resource=resource,
                    idem_resource_name=resource_id,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                    **uri_parameter_values,
                )
            )
    return result
