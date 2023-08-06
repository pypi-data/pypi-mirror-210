import copy
from typing import Any
from typing import Dict
from typing import List


def convert_raw_network_security_groups_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_id: str,
    resource_group_name: str,
    network_security_group_name: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Converts raw network_security_group api response into present function format

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        network_security_group_name: Azure Network Security group name.
        resource_id: Azure Policy Definition resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    translated_resource = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "network_security_group_name": network_security_group_name,
        "location": resource["location"],
    }
    if resource.get("tags"):
        translated_resource["tags"] = resource["tags"]
    if resource["properties"].get("securityRules"):
        translated_resource[
            "security_rules"
        ] = convert_raw_to_present_nsg_security_rule(
            hub, resource["properties"]["securityRules"]
        )
    return translated_resource


def convert_present_to_raw_network_security_groups(
    hub,
    location: str,
    security_rules: List = None,
    tags: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location: Resource location.
        security_rules: List of Security rules
        tags: Resource tags.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if tags is not None:
        payload["tags"] = tags
    if security_rules is not None:
        payload["properties"][
            "securityRules"
        ] = convert_present_to_raw_nsg_security_rule(hub, security_rules)
    return payload


def convert_present_to_raw_nsg_security_rule(
    hub, security_rules: List[Dict[str, Any]]
) -> List:
    """
    Converts security rule from present format to raw
    Args:
        security_rules: Raw security rules

    Returns:
        List
    """
    raw_security_rules = []
    for security_rule in security_rules:
        payload = {
            "name": security_rule["name"],
            "properties": {
                "protocol": security_rule["protocol"],
                "access": security_rule["access"],
                "priority": security_rule["priority"],
                "direction": security_rule["direction"],
            },
        }
        if security_rule.get("source_port_range"):
            payload["properties"]["sourcePortRange"] = security_rule[
                "source_port_range"
            ]
        if security_rule.get("source_port_ranges"):
            payload["properties"]["sourcePortRanges"] = security_rule[
                "source_port_ranges"
            ]
        if security_rule.get("destination_port_range"):
            payload["properties"]["destinationPortRange"] = security_rule[
                "destination_port_range"
            ]
        if security_rule.get("destination_port_ranges"):
            payload["properties"]["destinationPortRanges"] = security_rule[
                "destination_port_ranges"
            ]

        if security_rule.get("source_address_prefix"):
            payload["properties"]["sourceAddressPrefix"] = security_rule[
                "source_address_prefix"
            ]
        if security_rule.get("source_address_prefixes"):
            payload["properties"]["sourceAddressPrefixes"] = security_rule[
                "source_address_prefixes"
            ]
        if security_rule.get("destination_address_prefix"):
            payload["properties"]["destinationAddressPrefix"] = security_rule[
                "destination_address_prefix"
            ]
        if security_rule.get("destination_address_prefixes"):
            payload["properties"]["destinationAddressPrefixes"] = security_rule[
                "destination_address_prefixes"
            ]

        raw_security_rules.append(payload)
    return raw_security_rules


def convert_raw_to_present_nsg_security_rule(
    hub, security_rules: List[Dict[str, Any]]
) -> List:
    """
    Converts raw security rule to present function input format
    Args:
        security_rules: Raw security rules

    Returns:
        List
    """
    present_security_rules = []
    for security_rule in security_rules:
        payload = {
            "name": security_rule["name"],
            "priority": security_rule["properties"]["priority"],
            "direction": security_rule["properties"]["direction"],
            "access": security_rule["properties"]["access"],
            "protocol": security_rule["properties"]["protocol"],
        }
        if security_rule["properties"].get("sourcePortRange"):
            payload["source_port_range"] = security_rule["properties"][
                "sourcePortRange"
            ]
        if security_rule["properties"].get("sourcePortRanges"):
            payload["source_port_ranges"] = security_rule["properties"][
                "sourcePortRanges"
            ]
        if security_rule["properties"].get("destinationPortRange"):
            payload["destination_port_range"] = security_rule["properties"][
                "destinationPortRange"
            ]
        if security_rule["properties"].get("destinationPortRanges"):
            payload["destination_port_ranges"] = security_rule["properties"][
                "destinationPortRanges"
            ]

        if security_rule["properties"].get("sourceAddressPrefix"):
            payload["source_address_prefix"] = security_rule["properties"][
                "sourceAddressPrefix"
            ]
        if security_rule["properties"].get("sourceAddressPrefixes"):
            payload["source_address_prefixes"] = security_rule["properties"][
                "sourceAddressPrefixes"
            ]
        if security_rule["properties"].get("destinationAddressPrefix"):
            payload["destination_address_prefix"] = security_rule["properties"][
                "destinationAddressPrefix"
            ]
        if security_rule["properties"].get("destinationAddressPrefixes"):
            payload["destination_address_prefixes"] = security_rule["properties"][
                "destinationAddressPrefixes"
            ]
        present_security_rules.append(payload)
    return present_security_rules


def update_network_security_groups_payload(
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
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        need_update = True
    new_payload["properties"] = {}
    existing_properties = existing_payload["properties"]

    if new_values.get("security_rules") is not None:
        existing_security_rules = existing_properties.get("securityRules")
        existing_security_rules_required_payload = (
            convert_raw_to_present_nsg_security_rule(
                hub, security_rules=existing_security_rules
            )
        )
        if diff_nsg_security_rules(
            hub,
            new_values.get("security_rules"),
            existing_security_rules_required_payload,
            "name",
        ):
            new_payload["properties"][
                "securityRules"
            ] = convert_present_to_raw_nsg_security_rule(
                hub, security_rules=new_values.get("security_rules")
            )
            need_update = True

    if need_update:
        result["ret"] = new_payload
    return result


def diff_nsg_security_rules(
    hub,
    new_values: List[Dict[str, any]],
    old_values: List[Dict[str, any]],
    sorting_key: str,
):
    """
    Compares security rule variable and returns true if update is required.

    Args:
        new_values(List): List of new security rules
        old_values(List): List of new security rules
        sorting_key(str): Sorting key value

    Returns:
        bool
    """
    for entry in new_values:
        for key, value in entry.items():
            if isinstance(entry[key], list):
                entry[key].sort()

    for entry in old_values:
        for key, value in entry.items():
            if isinstance(entry[key], list):
                entry[key].sort()
    return sorted(new_values, key=lambda x: x[sorting_key]) != sorted(
        old_values, key=lambda x: x[sorting_key]
    )
