"""State module for managing Authorization Role Definitions."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    scope: str,
    role_definition_id: str,
    role_definition_name: str,
    permissions: List[
        make_dataclass(
            "ActionsSet",
            [
                ("actions", list, field(default=None)),
                ("notActions", list, field(default=None)),
                ("dataActions", list, field(default=None)),
                ("notDataActions", list, field(default=None)),
            ],
        )
    ],
    description: str = None,
    assignable_scopes: List[str] = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Role Definitions.

    Args:
        name(str): The identifier for this state.
        scope(str): The scope of the role definition.
        role_definition_id(str): The ID of the role definition.
        role_definition_name(str): The name of the role definition.
        permissions(list): The permissions of the role definitions.

            * actions(list, Optional):
                Allowed actions
            * notActions(list, Optional):
                Denied actions
            * dataActions(list, Optional):
                Allowed Data actions
            * notDataActions(list, Optional):
                Denied Data actions
        description(str): The description of the role definitions.
        assignable_scopes(list, Optional): The assignable scopes of the role definitions. Defaults to scope.
        resource_id(str, Optional): Role definition resource id on Azure.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            my-role-definition:
              azure.authorization.role_definitions.present:
                - name: my-role-definition
                - scope: /subscriptions/subscription-id
                - role_definition_id: aa246b4f-3ba8-4d39-8e43-687eb2e1661c
                - role_definition_name: my-role-name
                - permissions:
                  - actions:
                    - Microsoft.Resources/subscriptions/resourceGroups/read
                  - notActions:
                    - Microsoft.Resources/subscriptions/resourceGroups/write
                  - dataActions:
                    - Microsoft.Storage/storageAccounts/blobServices/containers/blobs/read
                  - notDataActions:
                    - Microsoft.Storage/storageAccounts/blobServices/containers/blobs/write
                - description: my-role-description
                - assignable_scopes:
                  - /subscriptions/subscription-id
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    if resource_id is None:
        resource_id = f"{scope}/providers/Microsoft.Authorization/roleDefinitions/{role_definition_id}"
    response_get = await hub.exec.azure.authorization.role_definitions.get(
        ctx, resource_id=resource_id, raw=True
    )

    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.authorization.role_definitions {response_get['comment']} {response_get['ret']}"
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
                    "scope": scope,
                    "role_definition_id": role_definition_id,
                    "resource_id": resource_id,
                    "role_definition_name": role_definition_name,
                    "description": description,
                    "permissions": permissions,
                    "assignable_scopes": assignable_scopes,
                },
            )
            result["comment"].append(
                f"Would create azure.authorization.role_definitions '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.authorization.role_definitions.convert_present_to_raw_role_definitions(
                scope=scope,
                role_definition_name=role_definition_name,
                description=description,
                permissions=permissions,
                assignable_scopes=assignable_scopes,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-04-01",
                success_codes=[201],
                json=payload,
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.authorization.role_definitions {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result
            result[
                "new_state"
            ] = hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                role_definition_id=role_definition_id,
                scope=scope,
                resource_id=resource_id,
            )
            result["comment"].append(
                f"Created azure.authorization.role_definitions '{name}'"
            )
            return result
    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            role_definition_id=role_definition_id,
            scope=scope,
            resource_id=resource_id,
        )
        new_payload = hub.tool.azure.authorization.role_definitions.update_role_definitions_payload(
            existing_resource,
            {
                "role_definition_name": role_definition_name,
                "description": description,
                "permissions": permissions,
                "assignable_scopes": assignable_scopes,
            },
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.authorization.role_definitions '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    role_definition_id=role_definition_id,
                    scope=scope,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Would update azure.authorization.role_definitions '{name}'"
                )
            return result

        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.authorization.role_definitions '{name}' has no property need to be updated."
            )
            return result
        result["comment"] = result["comment"] + new_payload["comment"]
        response_put = await hub.exec.request.json.put(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-04-01",
            success_codes=[200, 201],
            json=new_payload["ret"],
        )
        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.authorization.role_definitions {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_put["comment"], response_put["ret"]]
            return result

        result[
            "new_state"
        ] = hub.tool.azure.authorization.role_definitions.convert_raw_role_definitions_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            role_definition_id=role_definition_id,
            scope=scope,
            resource_id=resource_id,
        )
        result["comment"].append(
            f"Updated azure.authorization.role_definitions '{name}'"
        )
        return result


async def absent(hub, ctx, name: str, scope: str, role_definition_id: str) -> Dict:
    r"""Delete Role Definitions.

    Args:
        name(str): The identifier for this state.
        scope(str): The scope of the role definition.
        role_definition_id(str): The ID of the role definition to delete.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            my-role-definition:
              azure.authorization.role_definitions.absent:
                - name: my-role-definition
                - scope: /subscriptions/subscription-id
                - role_definition_id: aa246b4f-3ba8-4d39-8e43-687eb2e1661c
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    resource_id = f"{scope}/providers/Microsoft.Authorization/roleDefinitions/{role_definition_id}"
    response_get = await hub.exec.azure.authorization.role_definitions.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.authorization.role_definitions {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name
        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.authorization.role_definitions '{name}'"
            )
            return result

        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-04-01",
            success_codes=[200, 204],
        )
        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.authorization.role_definitions {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(
            f"Deleted azure.authorization.role_definitions '{name}'"
        )
        return result
    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.authorization.role_definitions '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Role Definitions under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.authorization.role_definitions
    """
    result = {}
    ret_list = await hub.exec.azure.authorization.role_definitions.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe authorization role_definitions {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.authorization.role_definitions.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
