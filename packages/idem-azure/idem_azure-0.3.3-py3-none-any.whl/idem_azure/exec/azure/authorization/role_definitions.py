"""Exec module for managing Authorization Role Definitions."""
from collections import OrderedDict
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(hub, ctx, resource_id: str, raw: bool = False) -> Dict[str, Any]:
    """Get authorization role definition resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of role definition
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.authorization.role_definitions.get resource_id="value"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.authorization.role_definitions.get
                - kwargs:
                    resource_id: "/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Authorization/roleDefinitions/{role_definition_name}"

    """
    result = dict(comment=[], result=True, ret=None)
    subscription_id = ctx.acct.subscription_id
    scope = f"/subscriptions/{subscription_id}"
    uri_parameters = OrderedDict({"roleDefinitions": "role_definition_id"})

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-04-01",
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
            ] = hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
                resource=response_get["ret"],
                idem_resource_name=resource_id,
                resource_id=resource_id,
                scope=scope,
                **uri_parameter_values,
            )

    return result


async def list_(hub, ctx) -> Dict:
    """List of authorization role definitions

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.authorization.role_definitions.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.authorization.role_definitions.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    scope = f"/subscriptions/{subscription_id}"
    uri_parameters = OrderedDict({"roleDefinitions": "role_definition_id"})

    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource in resource_list:
                resource_id = (
                    hub.tool.azure.authorization.role_definitions.get_resource_id(
                        resource
                    )
                )

                uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
                    resource_id, uri_parameters
                )
                result["ret"].append(
                    hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                        scope=scope,
                        **uri_parameter_values,
                    )
                )
    return result
