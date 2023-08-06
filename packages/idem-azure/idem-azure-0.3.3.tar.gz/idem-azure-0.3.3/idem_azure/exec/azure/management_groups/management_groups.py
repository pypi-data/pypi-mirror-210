"""Exec module for managing Management groups."""

__func_alias__ = {"list_": "list"}

from typing import Dict
from collections import OrderedDict


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict:
    """Gets Management group from azure account.

    Args:
        resource_id(str):
            The resource id of the Management group.
        raw(bool, Optional):
            Returns raw response if True. Defaults to False


    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.management_groups.management_groups.get resource_id="value" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.management_groups.management_groups.get
                - kwargs:
                    resource_id: "/providers/Microsoft.Management/managementGroups/{management_group_name}"
                    raw: False
    """

    result = dict(comment=[], ret=None, result=True)
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2020-05-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        # The response code is 404 or 403 means the management group does not exist or Authorization is failed
        if response_get["status"] not in [404, 403]:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result
    uri_parameters = OrderedDict({"managementGroups": "management_group_name"})
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )
    if raw:
        result["ret"] = response_get["ret"]
    else:
        result[
            "ret"
        ] = hub.tool.azure.management_groups.management_groups.convert_raw_management_group_to_present(
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
    """Lists all Management groups.

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id

        .. code-block:: bash

            idem exec azure.management_groups.management_groups.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.management_groups.management_groups.list

    """

    result = dict(comment=[], ret=[], result=True)

    uri_parameters = OrderedDict({"managementGroups": "management_group_name"})
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/providers/Microsoft.Management/managementGroups?api-version=2020-05-01",
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
                    hub.tool.azure.management_groups.management_groups.convert_raw_management_group_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                        **uri_parameter_values,
                    )
                )

    return result
