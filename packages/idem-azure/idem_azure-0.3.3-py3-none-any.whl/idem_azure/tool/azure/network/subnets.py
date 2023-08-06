import copy
from typing import Any
from typing import Dict
from typing import List


def update_subnets_payload(
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
    if (new_values.get("address_prefix") is not None) and (
        new_values["address_prefix"] != existing_properties.get("addressPrefix")
    ):
        new_payload["properties"]["addressPrefix"] = new_values.get("address_prefix")
        need_update = True
    if (
        new_values.get("enforce_private_link_endpoint_network_policies") is not None
    ) and (
        compare_policies(
            new_values["enforce_private_link_endpoint_network_policies"],
            existing_properties.get("privateEndpointNetworkPolicies"),
        )
    ):
        if new_values.get("enforce_private_link_endpoint_network_policies") is True:
            new_payload["properties"]["privateEndpointNetworkPolicies"] = "Enabled"
        elif new_values.get("enforce_private_link_endpoint_network_policies") is False:
            new_payload["properties"]["privateEndpointNetworkPolicies"] = "Disabled"
        need_update = True
    if new_values.get("delegations") is not None:
        if compare_delegations(
            new_values.get("delegations"),
            convert_raw_delegations_to_present(existing_properties.get("delegations")),
            "name",
        ):
            new_payload["properties"][
                "delegations"
            ] = convert_present_to_raw_delegations(new_values["delegations"])
            need_update = True
    if (
        new_values.get("enforce_private_link_service_network_policies") is not None
    ) and (
        compare_policies(
            new_values["enforce_private_link_service_network_policies"],
            existing_properties.get("privateLinkServiceNetworkPolicies"),
        )
    ):
        if new_values.get("enforce_private_link_service_network_policies") is True:
            new_payload["properties"]["privateLinkServiceNetworkPolicies"] = "Enabled"
        elif new_values.get("enforce_private_link_service_network_policies") is False:
            new_payload["properties"]["privateLinkServiceNetworkPolicies"] = "Disabled"
        need_update = True
    if (new_values.get("service_endpoints") is not None) and (
        (existing_properties.get("serviceEndpoints") is None)
        or (
            set(new_values["service_endpoints"])
            != {
                service_endpoint["service"]
                for service_endpoint in existing_properties.get("serviceEndpoints")
            }
        )
    ):
        new_payload["properties"]["serviceEndpoints"] = [
            {"service": service_name}
            for service_name in new_values["service_endpoints"]
        ]
        need_update = True
    if (new_values.get("service_endpoint_policy_ids") is not None) and (
        (existing_properties.get("serviceEndpointPolicies") is None)
        or (
            set(new_values["service_endpoint_policy_ids"])
            != {
                policy["id"]
                for policy in existing_properties.get("serviceEndpointPolicies")
            }
        )
    ):
        new_payload["properties"]["serviceEndpointPolicies"] = [
            {"id": policy_id} for policy_id in new_values["service_endpoint_policy_ids"]
        ]
        need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_subnets_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    virtual_network_name: str,
    subnet_name: str,
    resource_id: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        virtual_network_name: Azure Virtual Network resource name.
        subnet_name: Azure Subnet Resource name.
        resource_id: Azure Subnet resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "virtual_network_name": virtual_network_name,
        "subnet_name": subnet_name,
        "subscription_id": subscription_id,
    }
    properties = resource.get("properties")
    if properties:
        if properties.get("addressPrefix") is not None:
            resource_translated["address_prefix"] = properties.get("addressPrefix")
        if properties.get("privateEndpointNetworkPolicies") is not None:
            if properties.get("privateEndpointNetworkPolicies") == "Enabled":
                resource_translated[
                    "enforce_private_link_endpoint_network_policies"
                ] = True
            elif properties.get("privateEndpointNetworkPolicies") == "Disabled":
                resource_translated[
                    "enforce_private_link_endpoint_network_policies"
                ] = False
        if properties.get("privateLinkServiceNetworkPolicies") is not None:
            if properties.get("privateLinkServiceNetworkPolicies") == "Enabled":
                resource_translated[
                    "enforce_private_link_service_network_policies"
                ] = True
            elif properties.get("privateLinkServiceNetworkPolicies") == "Disabled":
                resource_translated[
                    "enforce_private_link_service_network_policies"
                ] = False
        if len(properties.get("delegations")) != 0:
            resource_translated["delegations"] = convert_raw_delegations_to_present(
                properties.get("delegations")
            )
        if properties.get("serviceEndpoints") is not None:
            resource_translated["service_endpoints"] = [
                service_endpoints["service"]
                for service_endpoints in properties.get("serviceEndpoints")
            ]
        if properties.get("serviceEndpointPolicies") is not None:
            resource_translated["service_endpoint_policy_ids"] = [
                service_endpoint_policy["id"]
                for service_endpoint_policy in properties.get("serviceEndpointPolicies")
            ]

    return resource_translated


def convert_present_to_raw_subnets(
    hub,
    address_prefix: str,
    enforce_private_link_endpoint_network_policies: bool = None,
    delegations: List = None,
    enforce_private_link_service_network_policies: bool = None,
    service_endpoints: List = None,
    service_endpoint_policy_ids: List = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        address_prefix: The address prefix for the subnet.
        enforce_private_link_endpoint_network_policies: Enable or Disable apply network policies on private end point in the subnet.
        delegations: An array of references to the delegations on the subnet.
        enforce_private_link_service_network_policies: Enable or Disable apply network policies on private link service in the subnet.
        service_endpoints: An array of service endpoints
        service_endpoint_policy_ids: An array of service endpoint policy Ids.
    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "properties": {"addressPrefix": address_prefix},
    }
    if enforce_private_link_endpoint_network_policies is not None:
        if enforce_private_link_endpoint_network_policies is True:
            payload["properties"]["privateEndpointNetworkPolicies"] = "Enabled"
        elif enforce_private_link_endpoint_network_policies is False:
            payload["properties"]["privateEndpointNetworkPolicies"] = "Disabled"
    if delegations is not None:
        payload["properties"]["delegations"] = convert_present_to_raw_delegations(
            delegations
        )
    if enforce_private_link_service_network_policies is not None:
        if enforce_private_link_service_network_policies is True:
            payload["properties"]["privateLinkServiceNetworkPolicies"] = "Enabled"
        elif enforce_private_link_service_network_policies is False:
            payload["properties"]["privateLinkServiceNetworkPolicies"] = "Disabled"
    if service_endpoints is not None:
        payload["properties"]["serviceEndpoints"] = [
            {"service": service_name} for service_name in service_endpoints
        ]
    if service_endpoint_policy_ids is not None:
        payload["properties"]["serviceEndpointPolicies"] = [
            {"id": policy_id} for policy_id in service_endpoint_policy_ids
        ]

    return payload


def convert_raw_delegations_to_present(delegations: List):
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
    present input parameters.

    Args:
        delegations(list[dict], optional): Resource List of Delegation in a subnet resource.

    Returns:
         A delegation List that contains the parameters that match respective present function's input format.
    """
    present_delegations: List = []
    for delegation in delegations:
        new_delegation_payload = {
            "name": delegation["name"],
            "service": delegation["properties"]["serviceName"],
        }
        present_delegations.append(new_delegation_payload)
    return present_delegations


def convert_present_to_raw_delegations(delegations: List):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        delegations(list[dict], required): List of Delegation in a subnet resource.Each Delegation will have fields
        ((name(str), required) and service(str), required))

    Returns:
        Delegations List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    raw_delegations: List = []
    for delegation in delegations:
        new_delegation_payload = {
            "name": delegation["name"],
            "properties": {"serviceName": delegation["service"]},
        }
        raw_delegations.append(new_delegation_payload)
    return raw_delegations


def compare_delegations(
    new_values: List[Dict[str, any]], resource: List[Dict[str, any]], sorting_key: str
):
    """
    Compares subnets delegations to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        new_values: (List[Dict[str, any]]) Present value which will be given as input
        resource: (List[Dict[str, any]]) Raw resource response which needs to be compared with new_values
        sorting_key: (str) Primary/Unique key name within each dictionary , which will be used to sort dictionary
         objects with given list before comparing.

    Returns:
        A boolean value, True if there is any difference between List[Dict] arguments else returns False
    """
    return sorted(new_values, key=lambda x: x[sorting_key]) != sorted(
        resource, key=lambda x: x[sorting_key]
    )


def compare_policies(new_values: bool, resource: str):
    """
    Compares subnets service policies and subnets endpoint policies to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        new_values: (bool) Present value which will be given as input
        resource: (str) Raw resource response which needs to be compared with new_values

    Returns:
        A boolean value, True if there is any difference between arguments else returns False
    """
    if (resource == "Disabled" and new_values == True) or (
        resource == "Enabled" and new_values == False
    ):
        return True
    return False
