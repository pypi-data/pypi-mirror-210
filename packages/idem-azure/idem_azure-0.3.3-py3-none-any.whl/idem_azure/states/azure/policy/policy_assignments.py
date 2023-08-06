"""State module for managing Policy Assignments."""
import copy
from typing import Any
from typing import Dict


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    scope: str,
    policy_assignment_name: str,
    policy_definition_id: str,
    parameters: Dict[str, Any] = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Policy Assignments.

    Args:
        name(str): The identifier for this state.
        scope(str): The scope of the policy assignment. Valid scopes are: management group (format: '/providers/Microsoft.Management/managementGroups/{managementGroup}'), subscription (format: '/subscriptions/{subscriptionId}'), resource group (format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}', or resource (format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/[{parentResourcePath}/]{resourceType}/{resourceName}'.
        policy_assignment_name(str): The name which should be used for this Policy Assignment. Changing this forces a new Resource Policy Assignment to be created.
        policy_definition_id(str): The ID of the Policy Definition or Policy Definition Set. Changing this forces a new Policy Assignment to be created
        parameters(dict[str, Any], Optional): Policy assignment parameters with respect to policy definition rule. Defaults to {}.
        resource_id(str, Optional): Policy Assignment resource id on Azure

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.policy.policy_assignments.present:
                - name: value
                - scope: value
                - policy_assignment_name: value
                - policy_definition_id: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if parameters is None:
        parameters = {}

    if resource_id is None:
        resource_id = f"{scope}/providers/Microsoft.Authorization/policyAssignments/{policy_assignment_name}"

    response_get = await hub.exec.azure.policy.policy_assignments.get(
        ctx, resource_id=resource_id, raw=True
    )

    if response_get["result"]:
        if not response_get["ret"]:
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "policy_assignment_name": policy_assignment_name,
                        "policy_definition_id": policy_definition_id,
                        "scope": scope,
                        "parameters": parameters,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.policy.policy_assignments '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.policy.policy_assignment.convert_present_to_raw_policy_assignment(
                    policy_definition_id=policy_definition_id,
                    parameters=parameters,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.policy.policy_assignments {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Created azure.policy.policy_assignments '{name}'"
                )
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_id=resource_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.policy.policy_assignment.update_policy_assignment_payload(
                existing_resource,
                {
                    "policy_definition_id": policy_definition_id,
                    "parameters": parameters,
                },
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.policy.policy_assignments '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_id=resource_id,
                    )
                    result["comment"].append(
                        f"Would update azure.policy.policy_assignments '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.policy.policy_assignments '{name}' has no property need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
                success_codes=[200, 201],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.policy.policy_assignments {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.policy.policy_assignment.convert_raw_policy_assignment_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_id=resource_id,
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.policy.policy_assignments '{name}' has no property need to be updated."
                )
                return result
            result["comment"].append(
                f"Updated azure.policy.policy_assignments '{name}'"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.policy.policy_assignments {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(hub, ctx, name: str, scope: str, policy_assignment_name: str) -> dict:
    r"""Delete Policy Assignment.

    Args:
        name(str): The identifier for this state.
        scope(str): The scope of the policy assignment. Valid scopes are: management group (format: '/providers/Microsoft.Management/managementGroups/{managementGroup}'), subscription (format: '/subscriptions/{subscriptionId}'), resource group (format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}', or resource (format: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/[{parentResourcePath}/]{resourceType}/{resourceName}'.
        policy_assignment_name(str): The name of the policy assignment to delete.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.policy.policy_assignments.absent:
                - name: value
                - scope: value
                - policy_assignment_name: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    resource_id = f"{scope}/providers/Microsoft.Authorization/policyAssignments/{policy_assignment_name}"

    response_get = await hub.exec.azure.policy.policy_assignments.get(
        ctx,
        resource_id=resource_id,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.policy.policy_assignments '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
                success_codes=[200, 202],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.policy.policy_assignments {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.policy.policy_assignments '{name}'"
            )
            return result

        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.policy.policy_assignments '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.policy.policy_assignments '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Policy Assignments under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.policy.policy_assignments
    """
    result = {}
    ret_list = await hub.exec.azure.policy.policy_assignments.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe policy assignment {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.policy.policy_assignments.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
