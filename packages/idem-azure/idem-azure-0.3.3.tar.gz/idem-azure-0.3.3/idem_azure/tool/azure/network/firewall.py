import copy
from typing import Any
from typing import Dict
from typing import List


def convert_raw_firewall_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    resource_id: str,
    firewall_name: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a Dict that match the format of
    present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        firewall_name: Azure firewall resource name.
        resource_id: Azure firewall resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
      A Dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "firewall_name": firewall_name,
        "location": resource["location"],
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    if "properties" in resource:
        resource_translated["properties"] = resource["properties"]
    if "type" in resource:
        resource_translated["type"] = resource["type"]
    if "zones" in resource:
        resource_translated["zones"] = resource["zones"]
    return resource_translated


def convert_present_to_raw_firewall(
    hub,
    tags: str,
    location: str,
    zones: str,
    sku: Dict[str, Any] = None,
    firewall_policy_id: str = None,
    ip_configuration: List[Dict[str, Any]] = None,
    management_ip_configuration: Dict[str, Any] = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        tags(Dict, Optional): Resource tags.
        location(str): Resource location. Changing this forces a new resource to be created.
        zones(str): A list of availability zones denoting where the resource needs to come from.
        sku(Dict, Optional): The SKU of the Firewall.
        firewall_policy_id(str): The ID of the Firewall Policy applied to this Firewall.
        ip_configuration(List(Dict), Optional): IP configuration of the Firewall.
        management_ip_configuration(Dict, Optional): Management IP configuration of the Firewall.
    Returns:
        A Dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if tags is not None:
        payload["tags"] = tags
    if zones is not None:
        payload["zones"] = zones
    if sku is not None:
        payload["properties"]["sku"] = {
            "name": sku.get("name"),
            "tier": sku.get("tier"),
        }
    if firewall_policy_id is not None:
        payload["properties"]["firewallPolicy"] = {"id": firewall_policy_id}
    if ip_configuration is not None:
        payload["properties"]["ipConfigurations"] = convert_present_to_ip_configuration(
            ip_configuration
        )
    if management_ip_configuration is not None:
        payload["properties"][
            "managementIpConfiguration"
        ] = convert_present_to_management_ip_configuration(management_ip_configuration)
    return payload


def convert_present_to_management_ip_configuration(
    management_ip_configuration: Dict[str, Any]
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        management_ip_configuration(Dict[str, Any]) : List of ip config payload for VM

    Returns:
        List of Management ip configurations payload Dict[str,any] in the format of an Azure PUT operation payload.
    """

    management_ip_config_payload = {
        "name": management_ip_configuration.get("name"),
        "properties": {
            "subnet": {"id": management_ip_configuration.get("subnet_id")},
            "publicIPAddress": {
                "id": management_ip_configuration.get("public_ip_address_id")
            },
        },
    }
    return management_ip_config_payload


def convert_present_to_ip_configuration(ip_configurations: List[Dict[str, Any]]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        ip_configurations(list(Dict[str, Any]) : List of ip config payload for VM

    Returns:
        List of ip configurations payload List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    data_ip_configuration_list: List = []
    for ip_config in ip_configurations:
        ip_config_payload = {
            "name": ip_config.get("name"),
            "properties": {
                "subnet": {"id": ip_config.get("subnet_id")},
                "publicIPAddress": {"id": ip_config.get("public_ip_address_id")},
            },
        }
        data_ip_configuration_list.append(ip_config_payload)
    return data_ip_configuration_list


def update_firewall_payload(
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
        A result Dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    need_update = False
    new_payload = copy.deepcopy(existing_payload)
    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        need_update = True
    new_payload.pop("properties", None)
    if need_update:
        result["ret"] = new_payload
    return result
