"""State module for managing Authorization Role Assignment."""
import copy
import uuid
from typing import Any
from typing import Dict


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    scope: str,
    role_definition_id: str,
    principal_id: str,
    resource_id: str = None,
    role_assignment_name: str = None,
) -> Dict[str, Any]:
    r"""Create or update Role Assignments.

    Args:
        name(str): The identifier for this state.
        scope(str): The scope of the role assignment to create. The scope can be any REST resource instance.
            For example, use '/subscriptions/{subscription-id}/' for a subscription,
            '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}' for a resource group,
            and '/subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/{resource-provider}/{resource-type}/{resource-name}' for a resource.
        role_definition_id(str): The role definition ID used in the role assignment.
        principal_id(str): The principal ID assigned to the role. This maps to the ID inside the Active Directory. It can point to a user, service principal, or security group.
        resource_id(str, Optional): Role Assignment resource id on Azure.
        role_assignment_name(str, Optional): A GUID for the role assignment to create. The name must be unique and different for each role assignment. This will be automatically generated if not specified.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.authorization.role_assignments.present:
                - name: value
                - scope: value
                - role_assignment_name: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    response_get = None

    if role_assignment_name:
        if resource_id is None:
            resource_id = f"{scope}/providers/Microsoft.Authorization/roleAssignments/{role_assignment_name}"

        response_get = await hub.exec.azure.authorization.role_assignments.get(
            ctx, resource_id=resource_id, raw=True
        )

    if response_get["result"]:
        if not response_get["ret"]:
            if role_assignment_name is None:
                role_assignment_name = uuid.uuid4()
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "scope": scope,
                        "role_assignment_name": role_assignment_name,
                        "resource_id": resource_id,
                        "role_definition_id": role_definition_id,
                        "principal_id": principal_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.authorization.role_assignments '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.authorization.role_assignments.convert_present_to_raw_role_assignments(
                    role_definition_id=role_definition_id,
                    principal_id=principal_id,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2015-07-01",
                    success_codes=[201],
                    json=payload,
                )

                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.authorization.role_assignments {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.authorization.role_assignments.convert_raw_role_assignments_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    role_assignment_name=role_assignment_name,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Created azure.authorization.role_assignments '{name}'"
                )
                return result
        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.authorization.role_assignments.convert_raw_role_assignments_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                role_assignment_name=role_assignment_name,
                resource_id=resource_id,
            )
            # No role assignment property can be updated without resource re-creation.
            result["comment"].append(
                f"azure.authorization.role_assignments '{name}' has no property to be updated."
            )
            result["new_state"] = copy.deepcopy(result["old_state"])
            return result
    else:
        hub.log.debug(
            f"Could not get azure.authorization.role_assignments {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub, ctx, name: str, scope: str, role_assignment_name: str, resource_id: str = None
) -> Dict[str, Any]:
    r"""Delete Role Assignments.

    Args:
        name(str): The identifier for this state.
        scope(str, Optional): The scope of the role assignment to delete.
        role_assignment_name(str, Optional): The name of the role assignment to delete.
        resource_id(str, Optional): Role assignment resource id on Azure. Either resource_id or a combination of scope
            and role_assignment_name need to be specified. Idem will automatically consider a resource as absent if both
            options are not specified.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.authorization.role_assignments.absent:
                - name: value
                - scope: value
                - role_assignment_name: value
    """
    result = dict(name=name, result=True, comment=[], old_state=None, new_state=None)
    if scope is not None and role_assignment_name is not None:
        constructed_resource_id = f"{scope}/providers/Microsoft.Authorization/roleAssignments/{role_assignment_name}"
        if resource_id is not None and resource_id != constructed_resource_id:
            result["result"] = False
            result["comment"].append(
                f"azure.authorization.role_assignments '{name}' resource_id {resource_id} does not match the constructed resource id"
            )
            return result
        resource_id = constructed_resource_id

    response_get = await hub.exec.azure.authorization.role_assignments.get(
        ctx,
        resource_id=resource_id,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.authorization.role_assignments '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}/{resource_id}?api-version=2015-07-01",
                success_codes=[200, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.authorization.role_assignments '{name}' {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.authorization.role_assignments '{name}'"
            )
            return result

        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.authorization.role_assignments '{name}' already absent"
            )
    else:
        hub.log.debug(
            f"Could not get azure.authorization.role_assignments '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Role Assignments under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.authorization.role_assignments
    """
    result = {}
    ret_list = await hub.exec.azure.authorization.role_assignments.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe role assignment {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.authorization.role_assignments.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
