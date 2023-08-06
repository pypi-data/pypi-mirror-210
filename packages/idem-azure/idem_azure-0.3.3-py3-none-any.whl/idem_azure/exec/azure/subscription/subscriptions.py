"""Exec module for managing Subscriptions."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict[str, Any]:
    """Get subscription resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of subscription.
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.subscription.subscriptions.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.subscription.subscriptions.get
                - kwargs:
                    resource_id: "/providers/Microsoft.Subscription/aliases/{alias}"

    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict({"aliases": "alias"})

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-09-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if not response_get["ret"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result

    elif response_get["result"] and response_get["ret"]:
        subscription_id = response_get["ret"]["properties"]["subscriptionId"]
        response_get_detailed_subscription = await hub.exec.request.json.get(
            ctx,
            url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}?api-version=2020-01-01",
            success_codes=[200],
        )
        if not response_get_detailed_subscription["result"]:
            result["result"] = False
            result["comment"] = response_get_detailed_subscription["comment"]
            return result
        else:
            if raw:
                result["ret"] = response_get_detailed_subscription["ret"]
            else:
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                result[
                    "ret"
                ] = hub.tool.azure.subscription.subscriptions.convert_raw_subscription_to_present(
                    resource=response_get_detailed_subscription["ret"],
                    idem_resource_name=resource_id,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                    display_name=None,
                    **uri_parameter_values,
                )

    return result


async def list_(hub, ctx) -> Dict:
    """List of subscriptions

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.subscription.subscriptions.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.subscription.subscriptions.list


    """
    result = dict(comment=[], result=True, ret=[])
    uri_parameters = OrderedDict({"subscriptions": "subscription_id"})
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx['acct']['endpoint_url']}/subscriptions?api-version=2020-01-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value", None)
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource["id"], uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.subscription.subscriptions.convert_raw_subscription_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                        alias=None,
                        display_name=None,
                        **uri_parameter_values,
                    )
                )

    return result
