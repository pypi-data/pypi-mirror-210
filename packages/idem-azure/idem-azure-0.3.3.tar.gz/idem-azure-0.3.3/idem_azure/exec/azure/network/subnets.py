"""Exec module for managing subnets."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict[str, Any]:
    """Get subnet resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of subnet
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.network.subnets.get resource_id="value"  raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.subnets.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/subnets/{subnet_name}"
                    raw: False
    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "virtualNetworks": "virtual_network_name",
            "subnets": "subnet_name",
        }
    )

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{hub.exec.azure.URL}{resource_id}?api-version=2021-06-01",
        success_codes=[200, 201],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result

    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )
    if raw:
        result["ret"] = response_get["ret"]

    else:
        result["ret"] = hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
            resource=response_get["ret"],
            idem_resource_name=resource_id,
            resource_id=resource_id,
            **uri_parameter_values,
        )

    return result


async def list_(hub, ctx) -> Dict:
    """List of subnets

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.network.subnets.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.network.subnets.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "virtualNetworks": "virtual_network_name",
            "subnets": "subnet_name",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Network/virtualNetworks?api-version=2021-03-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for vnet in resource_list:
                if vnet.get("properties") and vnet.get("properties").get("subnets"):
                    subnet_list = vnet["properties"]["subnets"]
                    for resource in subnet_list:
                        resource_id = resource["id"]
                        uri_parameter_values = (
                            hub.tool.azure.uri.get_parameter_value_in_dict(
                                resource_id, uri_parameters
                            )
                        )
                        result["ret"].append(
                            hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
                                resource=resource,
                                idem_resource_name=resource_id,
                                subscription_id=subscription_id,
                                resource_id=resource_id,
                                **uri_parameter_values,
                            )
                        )

    return result
