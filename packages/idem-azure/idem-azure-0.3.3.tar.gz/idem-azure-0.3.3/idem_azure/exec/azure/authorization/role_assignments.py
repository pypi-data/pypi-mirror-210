"""Exec module for managing Authorization Role Assignments."""
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
    """Get role assignment from resource_id.

    Args:
        resource_id(str):
            The resource_id of role assignment
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.authorization.role_assignments.get resource_id="value"  raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.network.public_ip_addresses.get
                - kwargs:
                    name: "my_resource"
                    resource_id: "{scope}/providers/Microsoft.Authorization/roleAssignments/{role_assignment_name}"
                    raw: False

    """

    result = dict(comment=[], ret=None, result=True)

    uri_parameters = OrderedDict({"roleAssignments": "role_assignment_name"})
    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}/{resource_id}?api-version=2015-07-01",
        success_codes=[200],
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
        result[
            "ret"
        ] = hub.tool.azure.authorization.role_assignments.convert_raw_role_assignments_to_present(
            resource=response_get["ret"],
            idem_resource_name=resource_id,
            role_assignment_name=uri_parameter_values["role_assignment_name"],
            resource_id=resource_id,
        )

    return result


async def list_(hub, ctx) -> Dict:
    """List of role assignment

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.authorization.role_assignments.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.authorization.role_assignments.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    uri_parameters = OrderedDict({"roleAssignments": "role_assignment_name"})
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Authorization/roleAssignments?api-version=2015-07-01",
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
                    hub.tool.azure.authorization.role_assignments.convert_raw_role_assignments_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        role_assignment_name=uri_parameter_values[
                            "role_assignment_name"
                        ],
                        resource_id=resource_id,
                    )
                )
    return result
