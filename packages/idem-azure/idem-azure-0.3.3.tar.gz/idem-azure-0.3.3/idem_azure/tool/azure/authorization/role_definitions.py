import copy
from typing import Any
from typing import Dict
from typing import List


def update_role_definitions_payload(
    hub, existing_payload: Dict[str, Any], new_values: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
     PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        existing_payload: An existing resource state from Azure. This is usually a GET operation response.
        new_values: A dictionary of desired state values. If any property's value is None,
         this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
         do an update.

    Returns:
        A result dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages tuple.
    """
    result = {"result": True, "ret": None, "comment": []}
    need_update = False
    new_payload = copy.deepcopy(existing_payload)
    existing_properties = existing_payload["properties"]
    if (new_values.get("role_definition_name") is not None) and (
        new_values["role_definition_name"] != existing_properties.get("roleName")
    ):
        new_payload["properties"]["roleName"] = new_values.get("role_definition_name")
        need_update = True
    if (new_values.get("description") is not None) and (
        new_values["description"] != existing_properties.get("description")
    ):
        new_payload["properties"]["description"] = new_values.get("description")
        need_update = True
    if (new_values.get("permissions") is not None) and (
        compare_permissions(
            new_values["permissions"], existing_properties.get("permissions"), "actions"
        )
    ):
        new_payload["properties"]["permissions"] = new_values.get("permissions")
        need_update = True
    if (new_values.get("assignable_scopes") is not None) and (
        set(new_values["assignable_scopes"])
        != set(existing_properties.get("assignableScopes"))
    ):
        new_payload["properties"]["assignableScopes"] = new_values["assignable_scopes"]
        need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_role_definitions_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    role_definition_id: str,
    scope: str,
    resource_id: str,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        role_definition_id: Azure role definition resource id.
        scope: scope of the resource.
        resource_id: Role definition resource id on Azure.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "role_definition_id": role_definition_id,
        "scope": scope,
    }
    properties = resource.get("properties")
    if properties:
        properties_parameters = {
            "roleName": "role_definition_name",
            "permissions": "permissions",
            "assignableScopes": "assignable_scopes",
        }
        for parameter_raw, parameter_present in properties_parameters.items():
            if parameter_raw in properties:
                resource_translated[parameter_present] = properties[parameter_raw]
        if properties.get("description") is not None:
            resource_translated["description"] = properties.get("description")
    return resource_translated


def convert_present_to_raw_role_definitions(
    hub,
    scope: str,
    role_definition_name: str,
    permissions: List[str],
    description: str = None,
    assignable_scopes: List[str] = None,
) -> Dict[str, Any]:
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        scope: The scope of the role definition.
        role_definition_name: The role definition name used in the role definition.
        permissions: The permissions of the role definitions.
        description: The description of the role definitions.
        assignable_scopes: The assignable scopes of the role definitions.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "properties": {
            "roleName": role_definition_name,
            "permissions": permissions,
        }
    }
    if description is not None:
        payload["properties"]["description"] = description
    if assignable_scopes is not None:
        payload["properties"]["assignableScopes"] = assignable_scopes
    else:
        payload["properties"]["assignableScopes"] = [scope]
    return payload


def compare_permissions(
    new_values: List[Dict[str, any]], resource: List[Dict[str, any]], sorting_key: str
):
    """
    Compares role definition permissions to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        new_values: (List[Dict[str, any]]) Present value which will be given as input.
        resource: (List[Dict[str, any]]) Raw resource response which needs to be compared with new_values.
        sorting_key: (str) Primary/Unique key name within each dictionary , which will be used to sort dictionary
         objects with given list before comparing.

    Returns:
        A boolean value, True if there is any difference between List[Dict] arguments else returns False.
    """
    new_values = sorted(new_values, key=lambda x: x[sorting_key])
    resource_list = sorted(resource, key=lambda x: x[sorting_key])
    for i in range(len(resource_list)):
        for key, value in resource_list[i].items():
            if new_values[i].get(key) is None or new_values[i][key] != value:
                return True
    return False


def get_resource_id(hub, resource: Dict[str, any]):
    """
    Returns the resource_id based on the role_definition type if built in role_definition removing the subscription scope from resource_id
    Args:
        resource: (list[dict[str, any]]) Raw resource response which needs to be compared with new_values.

    Returns:
        A string value of resource_id
    """
    resource_id = resource.get("id")
    if resource.get("properties"):
        if (
            resource["properties"].get("type") == "BuiltInRole"
            and resource_id.find("/providers") != -1
        ):
            resource_id = resource_id[resource_id.index("/providers") :]
            hub.log.debug(
                f"Role Definition resource id is being rewritten from {resource['id']} to {resource_id}."
            )
    return resource_id
