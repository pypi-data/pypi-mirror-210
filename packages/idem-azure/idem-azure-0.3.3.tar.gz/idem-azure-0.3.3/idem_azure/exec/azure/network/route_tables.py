"""Exec module for managing Network Route Tables"""

__func_alias__ = {"list_": "list"}

from typing import Dict
from collections import OrderedDict


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict:
    """Gets network Route table from azure account.

    Args:
        resource_id(str):
            The resource id of the Route table.
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.route_tables.get resource_id="value" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.route_tables.get
                - kwargs:
                     resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/routeTables/{route_table_name}"
                     raw: False
    """

    result = dict(comment=[], ret=None, result=True)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "routeTables": "route_table_name",
        }
    )
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )
    if raw:
        result["ret"] = response_get["ret"]
    else:
        result[
            "ret"
        ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
            idem_resource_name=resource_id,
            resource=response_get["ret"],
            resource_id=resource_id,
            **uri_parameter_values,
        )
    return result


async def list_(
    hub,
    ctx,
) -> Dict:
    """Lists all Network Route Tables.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.network.route_tables.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.network.route_tables.list

    """

    result = dict(comment=[], ret=[], result=True)

    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "routeTables": "route_table_name",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Network/routeTables?api-version=2022-07-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value", None)
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                        **uri_parameter_values,
                    )
                )

    return result
