"""State module for managing Policy Definition."""
import copy
from typing import Any
from typing import Dict


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    policy_definition_name: str,
    policy_type: str,
    mode: str,
    subscription_id: str = None,
    display_name: str = None,
    description: str = None,
    policy_rule: Dict = None,
    metadata: Dict = None,
    parameters: Dict = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Policy Definitions.

    Args:
        name(str): The identifier for this state.
        policy_definition_name(str): The name of the policy Definition.
        policy_type(str): The policy type. Possible values are BuiltIn, Custom and NotSpecified.
        mode(str): The policy mode that allows you to specify which resource types will be evaluated.
                   Some examples are All, Indexed, Microsoft.KeyVault.Data.
        subscription_id(str, Optional): Subscription Unique id.
        display_name(str): The display name of the policy definition.
        description(str, Optional): The description of the policy definition.
        policy_rule(dict, Optional): The policy rule for the policy definition.
        metadata(dict, Optional): The metadata for the policy definition.
        parameters(dict, Optional): Parameters for the policy definition.
        resource_id(str, Optional): Policy Definition resource id on Azure

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            policy_definition_is_present:
              azure.policy.policy_definitions.present:
                - name: value
                - policy_definition_name: value
                - subscription_id: value
                - policy_type: value
                - mode: value
                - display_name: value
                - description: value
                - metadata:
                        version: 1.0.0
                        category: RoleDefinitions
                - parameters:
                    roleDefinitionIds:
                        type: Array
                        metadata:
                            displayName: Approved Role Definitions
                            description: The list of role definition Ids.
                            strongType: roleDefinitionIds
                - policy_rule:
                        if:
                          allOf:
                            - field: type
                              equals: Microsoft.Authorization/roleAssignments
                            - not:
                                field: Microsoft.Authorization/roleAssignments/roleDefinitionId
                                in: "[parameters('roleDefinitionIds')]"
                        then:
                      effect: deny

    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    if resource_id is None:
        resource_id = f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/policyDefinitions/{policy_definition_name}"
    response_get = await hub.exec.azure.policy.policy_definitions.get(
        ctx, resource_id=resource_id, raw=True
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.policy.policy_definitions {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if not response_get["ret"]:
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "policy_definition_name": policy_definition_name,
                    "subscription_id": subscription_id,
                    "policy_type": policy_type,
                    "mode": mode,
                    "display_name": display_name,
                    "description": description,
                    "policy_rule": policy_rule,
                    "metadata": metadata,
                    "parameters": parameters,
                    "resource_id": resource_id,
                },
            )
            result["comment"].append(
                f"Would create azure.policy.policy_definitions '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.policy.policy_definition.convert_present_to_raw_policy_definition(
                policy_type=policy_type,
                description=description,
                display_name=display_name,
                mode=mode,
                metadata=metadata,
                policy_rule=policy_rule,
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
                    f"Could not create Policy Definitions {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.policy.policy_definition.convert_raw_policy_definition_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                policy_definition_name=policy_definition_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(
                f"Created azure.policy.policy_definitions '{name}'"
            )
            return result

    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.policy.policy_definition.convert_raw_policy_definition_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            policy_definition_name=policy_definition_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        # Generate a new PUT operation payload with new values
        new_payload = (
            hub.tool.azure.policy.policy_definition.update_policy_definition_payload(
                existing_resource,
                {
                    "policy_type": policy_type,
                    "display_name": display_name,
                    "description": description,
                    "mode": mode,
                    "policy_rule": policy_rule,
                    "metadata": metadata,
                    "parameters": parameters,
                },
            )
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.policy.policy_definitions '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.policy.policy_definition.convert_raw_policy_definition_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    policy_definition_name=policy_definition_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Would update azure.policy.policy_definitions '{name}'"
                )
            return result

        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.policy.policy_definitions '{name}' has no property need to be updated."
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
                f"Could not update azure.policy.policy_definitions {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_put["comment"], response_put["ret"]]
            return result

        result[
            "new_state"
        ] = hub.tool.azure.policy.policy_definition.convert_raw_policy_definition_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            policy_definition_name=policy_definition_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        result["comment"].append(f"Updated azure.policy.policy_definitions '{name}'")
        return result


async def absent(
    hub, ctx, name: str, policy_definition_name: str, subscription_id: str = None
) -> Dict:
    r"""Delete Policy Definition.

    Args:
        name(str): The identifier for this state.
        policy_definition_name(str): The name of the policy definition to delete.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.policy.policy_definitions.absent:
                - name: value
                - policy_definition_name: value
                - subscription_id: value
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }

    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/policyDefinitions/{policy_definition_name}"
    response_get = await hub.exec.azure.policy.policy_definitions.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.policy.policy_definitions '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name

        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.policy.policy_definitions '{name}'"
            )
            return result
        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
            success_codes=[200, 202],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.policy.policy_definitions {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(f"Deleted azure.policy.policy_definitions '{name}'")
        return result
    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.policy.policy_definitions '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Policy Definitions under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.policy.policy_definitions
    """
    result = {}
    ret_list = await hub.exec.azure.policy.policy_definitions.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe policy policy_definitions {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.policy.policy_definitions.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
