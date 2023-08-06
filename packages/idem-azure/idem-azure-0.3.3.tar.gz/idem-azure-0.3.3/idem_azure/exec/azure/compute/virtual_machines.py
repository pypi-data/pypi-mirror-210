"""Exec module for managing Compute Virtual Machines."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict[str, Any]:
    """Get compute virtual machines resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of virtual machine
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.compute.virtual_machines.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"

    """
    result = dict(comment=[], result=True, ret=None)
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "virtualMachines": "virtual_machine_name",
        }
    )

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{hub.exec.azure.URL}{resource_id}?api-version=2022-03-01",
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
            ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                resource=response_get["ret"],
                idem_resource_name=resource_id,
                resource_id=resource_id,
                **uri_parameter_values,
            )

    return result


async def list_(hub, ctx) -> Dict:
    """List of compute virtual machines

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.compute.virtual_machines.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.compute.virtual_machines.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict(
        {
            "resourceGroups": "resource_group_name",
            "virtualMachines": "virtual_machine_name",
        }
    )
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Compute/virtualMachines?api-version=2022-03-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        subscription_id=subscription_id,
                        resource_id=resource_id,
                        **uri_parameter_values,
                    )
                )
    return result
