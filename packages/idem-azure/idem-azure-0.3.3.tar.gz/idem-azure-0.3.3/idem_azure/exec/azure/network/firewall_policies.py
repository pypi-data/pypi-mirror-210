"""Exec module for managing Firewall Policy."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(
    hub,
    ctx,
    resource_id: str,
    raw: bool = False,
) -> Dict[str, Any]:
    """Get firewall policy resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of firewall policy
        raw(bool):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.network.firewall_policies.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.firewall_policies.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/firewallPolicies/{firewall_policy_name}"

    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "subscriptions": "subscription_id",
            "firewallPolicies": "firewall_policy_name",
        }
    )

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{hub.exec.azure.URL}{resource_id}?api-version=2022-07-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result

    elif response_get["result"] and response_get["ret"]:
        if raw:
            result["ret"] = response_get["ret"]

        else:
            uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                resource_id, uri_parameters
            )
            result[
                "ret"
            ] = hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
                resource=response_get["ret"],
                idem_resource_name=resource_id,
                resource_id=resource_id,
                **uri_parameter_values,
            )

    return result


async def list_(hub, ctx) -> Dict:
    """List of firewall policies

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.network.firewall_policies.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.network.firewall_policies


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "subscriptions": "subscription_id",
            "firewallPolicies": "firewall_policy_name",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Network/firewallPolicies?api-version=2022-07-01",
        success_codes=[200],
    ):
        firewall_policy_list = page_result.get("value")
        if firewall_policy_list:
            for resource in firewall_policy_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource["id"], uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                        **uri_parameter_values,
                    )
                )
    return result
