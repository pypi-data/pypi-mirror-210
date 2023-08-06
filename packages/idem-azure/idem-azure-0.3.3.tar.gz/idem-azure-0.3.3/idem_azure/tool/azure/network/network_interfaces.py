import copy
from typing import Any
from typing import Dict
from typing import List


def update_network_interfaces_payload(
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
    if (new_values.get("tags") is not None) and (
        new_values.get("tags") != existing_payload.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        need_update = True
    existing_properties = existing_payload["properties"]

    if new_values.get("ip_configurations") is not None:
        existing_ip_configurations = existing_properties.get("ipConfigurations")
        existing_ip_configurations_payload = convert_raw_ip_configurations_to_present(
            ip_configurations=existing_ip_configurations
        )

        if diff_network_ip_configurations(
            new_values.get("ip_configurations"),
            existing_ip_configurations_payload,
            "name",
        ):
            new_payload["properties"][
                "ipConfigurations"
            ] = convert_present_ip_configurations_to_raw(
                ip_configurations=new_values.get("ip_configurations")
            )
            need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_network_interfaces_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    network_interface_name: str,
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
        network_interface_name: Azure Network Interface name.
        resource_id: Azure Policy Definition resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "network_interface_name": network_interface_name,
        "location": resource["location"],
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    properties = resource.get("properties")
    if properties.get("ipConfigurations") is not None:
        existing_ip_configurations_payload = convert_raw_ip_configurations_to_present(
            ip_configurations=properties["ipConfigurations"]
        )
        resource_translated["ip_configurations"] = existing_ip_configurations_payload
    return resource_translated


def convert_present_to_raw_network_interfaces(
    hub,
    location: str,
    ip_configurations: List[Dict[str, Any]],
    tags: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location: Resource location.
        ip_configurations: A list of IPConfigurations of the network interface.
           Each ip configuration supports fields  ((name(str), required),
           (subnet_id(str, optional), (private_ip_address_version(str, optional),
           (private_ip_address_allocation(str, optional), private_ip_address(str, optional)
           and primary (boolean, optional)).
        tags: Resource tags.
    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "location": location,
    }
    if tags is not None:
        payload["tags"] = tags
    if ip_configurations is not None:
        ip_configurations_payload = convert_present_ip_configurations_to_raw(
            ip_configurations
        )
        payload["properties"] = {}
        payload["properties"]["ipConfigurations"] = ip_configurations_payload

    return payload


def convert_raw_ip_configurations_to_present(ip_configurations: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        ip_configurations(List[Dict[str, Any]]): A list of IPConfigurations of the network interface.

    Returns:
         An ip_configurations List that contains the parameters that match respective present function's input format.
    """
    present_ip_configurations: List = []
    for ip_configuration in ip_configurations:
        existing_ip_configuration_payload = {
            "name": ip_configuration.get("name"),
            "private_ip_address_allocation": ip_configuration["properties"][
                "privateIPAllocationMethod"
            ],
        }
        if ip_configuration["properties"].get("subnet") is not None:
            existing_ip_configuration_payload["subnet_id"] = ip_configuration[
                "properties"
            ]["subnet"]["id"]
        if ip_configuration["properties"].get("privateIPAddressVersion") is not None:
            existing_ip_configuration_payload[
                "private_ip_address_version"
            ] = ip_configuration["properties"]["privateIPAddressVersion"]
        if ip_configuration["properties"].get("privateIPAddress") is not None:
            existing_ip_configuration_payload["private_ip_address"] = ip_configuration[
                "properties"
            ]["privateIPAddress"]
        if ip_configuration["properties"].get("primary") is not None:
            existing_ip_configuration_payload["primary"] = ip_configuration[
                "properties"
            ]["primary"]
        present_ip_configurations.append(existing_ip_configuration_payload)
    return present_ip_configurations


def convert_present_ip_configurations_to_raw(ip_configurations: List[Dict[str, Any]]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        ip_configurations(List[Dict[str, Any]], required): A list of IPConfigurations of the network interface.
          Each ip configuration supports fields  ((name(str), required),
          (subnet_id(str, optional), (private_ip_address_version(str, optional),
          (private_ip_address_allocation(str, optional), private_ip_address(str, optional)
          and primary (boolean, optional)).

    Returns:
        ipConfigurations List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    raw_ip_configurations: List = []
    for ip_configuration in ip_configurations:
        payload = {
            "name": ip_configuration["name"],
            "properties": {},
        }
        if ip_configuration.get("private_ip_address_allocation") is not None:
            payload["properties"]["privateIPAllocationMethod"] = ip_configuration[
                "private_ip_address_allocation"
            ]
        if ip_configuration.get("subnet_id") is not None:
            payload["properties"]["subnet"] = {"id": ip_configuration["subnet_id"]}
        if ip_configuration.get("private_ip_address_version") is not None:
            payload["properties"]["privateIPAddressVersion"] = ip_configuration[
                "private_ip_address_version"
            ]
        if ip_configuration.get("private_ip_address") is not None:
            payload["properties"]["privateIPAddress"] = ip_configuration[
                "private_ip_address"
            ]
        if ip_configuration.get("primary") is not None:
            payload["properties"]["primary"] = ip_configuration["primary"]
        raw_ip_configurations.append(payload)
    return raw_ip_configurations


def diff_network_ip_configurations(
    new_values: List[Dict[str, any]], resource: List[Dict[str, any]], sorting_key: str
):
    """
    Compares network interface ip configurations to check whether any of the state attributes has been added or modified.
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
