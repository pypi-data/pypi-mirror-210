"""Exec module for managing policy assignments."""
from typing import Any
from typing import Dict

__func_alias__ = {"list_": "list"}


async def get(
    hub,
    ctx,
    resource_id: str,
    raw: bool = False,
) -> Dict[str, Any]:
    """Get policy assignments resource from resource_id.

    Args:
        resource_id(str):
            The resource_id of policy assignments
        raw(bool, Optional):
            Returns raw response if True. Defaults to False

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.policy.policy_assignments.get resource_id="value" raw="False"

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path:  azure.policy.policy_assignments.get
                - kwargs:
                    resource_id: "{scope}/providers/Microsoft.Authorization/policyAssignments/{policy_assignment_name}"
                    raw: False

    """
    result = dict(comment=[], result=True, ret=None)

    response_get = await hub.exec.request.json.get(
        ctx,
        url=f"{hub.exec.azure.URL}{resource_id}?api-version=2021-06-01",
        success_codes=[200],
    )
    if not response_get["result"]:
        if response_get["status"] != 404:
            result["result"] = False
        result["comment"] = response_get["comment"]
        return result

    if raw:
        result["ret"] = response_get["ret"]

    else:
        result[
            "ret"
        ] = hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
            resource=response_get["ret"],
            idem_resource_name=resource_id,
            resource_id=resource_id,
        )

    return result


async def list_(hub, ctx) -> Dict:
    """List of policy assignments

    Returns:
        Dict[str, Any]

    Examples:
        Calling this exec module function from the cli with resource_id:

        .. code-block:: bash

            idem exec azure.policy.policy_assignments.list

        Using in a state:

        .. code-block:: yaml

            my_unmanaged_resource:
              exec.run:
                - path: azure.policy.policy_assignments1.list


    """
    result = dict(comment=[], result=True, ret=[])
    subscription_id = ctx.acct.subscription_id
    async for page_result in hub.tool.azure.request.paginate(
        ctx,
        url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}"
        f"/providers/Microsoft.Authorization/policyAssignments?api-version=2021-06-01",
        success_codes=[200],
    ):
        resource_list = page_result.get("value")
        if resource_list:
            for resource in resource_list:
                resource_id = resource["id"]
                result["ret"].append(
                    hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
                        resource=resource,
                        idem_resource_name=resource_id,
                        resource_id=resource_id,
                    )
                )
    return result
