import copy
from typing import Any
from typing import Dict

from dict_tools.differ import deep_diff


def update_policy_assignment_payload(
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
    if new_values.get("parameters") is not None and deep_diff(
        new_values["parameters"], existing_properties.get("parameters")
    ):
        new_payload["properties"]["parameters"] = new_values.get("parameters")
        need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_policy_assignment_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_id: str,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_id: Azure Policy Definition resource id.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "policy_assignment_name": resource.get("name"),
    }
    properties = resource.get("properties")
    if properties:
        properties_parameters = {
            "policyDefinitionId": "policy_definition_id",
            "scope": "scope",
            "parameters": "parameters",
        }
        for parameter_raw, parameter_present in properties_parameters.items():
            if parameter_raw in properties:
                resource_translated[parameter_present] = properties.get(parameter_raw)
    return resource_translated


def convert_present_to_raw_policy_assignment(
    hub,
    policy_definition_id: str,
    parameters: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        policy_definition_id(str): The ID of the Policy Definition or Policy Definition Set. Changing this forces a new Policy Assignment to be created
        parameters(dict, optional): API request payload parameters. Defaults to {}.
    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"properties": {"policyDefinitionId": policy_definition_id}}
    if parameters is not None:
        payload["properties"]["parameters"] = parameters
    return payload
