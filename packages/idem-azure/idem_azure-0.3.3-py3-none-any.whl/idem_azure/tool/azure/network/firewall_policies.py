import copy
from typing import Any
from typing import Dict


def convert_raw_firewall_policies_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    resource_id: str,
    firewall_policy_name: str,
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
        firewall_policy_name: Azure firewall policy resource name.
        resource_id: Azure Virtual Machine resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
      A Dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "firewall_policy_name": firewall_policy_name,
        "location": resource["location"],
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    if "properties" in resource:
        resource_translated["properties"] = resource["properties"]
    if "type" in resource:
        resource_translated["type"] = resource["type"]
    return resource_translated


def convert_present_to_raw_fire_policies(
    hub,
    tags: str,
    location: str,
    dns_settings: Dict[str, Any] = None,
    sku: Dict[str, Any] = None,
    intrusion_detection: Dict[str, Any] = None,
    threat_intelligence_mode: str = None,
    threat_intelligence_allow_list: Dict[str, Any] = None,
    base_policy_id: str = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        tags(Dict, Optional): Resource tags.
        location(str): Resource location. Changing this forces a new resource to be created.
        dns_settings(Dict): Specifies the dns proxy and server of the firewall policy.
        sku(Dict): Specifies the SKU Tier of the Firewall Policy.
        intrusion_detection(Dict): Specifies the intrusion_detection block for Firewall policy.
        threat_intelligence_mode(str):The operation mode for Threat Intelligence. Possible values are Alert, Deny and Off. Defaults to Alert.
        threat_intelligence_allow_list(Dict): Specifies threat_intelligence_allowlist while creating the Firewall policy.
        base_policy_id(str): The ID of the base Firewall Policy.

    Returns:
        A Dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if tags is not None:
        payload["tags"] = tags
    if dns_settings is not None:
        payload["properties"]["dnsSettings"] = convert_present_to_raw_dns(dns_settings)
    if threat_intelligence_allow_list is not None:
        payload["properties"][
            "threatIntelWhitelist"
        ] = convert_present_to_raw_threat_intelligence_allowlist(
            threat_intelligence_allow_list
        )
    if sku is not None:
        payload["properties"]["sku"] = {"tier": sku.get("tier")}
    if intrusion_detection is not None:
        payload["properties"]["intrusionDetection"] = {
            "mode": intrusion_detection.get("mode")
        }
    if base_policy_id is not None:
        payload["properties"]["basePolicy"] = {"id": base_policy_id}
    if threat_intelligence_mode is not None:
        payload["properties"]["threatIntelMode"] = threat_intelligence_mode
    return payload


def convert_present_to_raw_threat_intelligence_allowlist(
    threat_intelligence_allow_list: Dict[str, Any]
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        threat_intelligence_allow_list(list(str)) : List of allowed Threat Intelligence

    Returns:
        Threat white list payload(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    threat_white_list_payload = {}
    if threat_intelligence_allow_list.get("fqdns") is not None:
        threat_white_list_payload["fqdns"] = threat_intelligence_allow_list.get("fqdns")
    if threat_intelligence_allow_list.get("ip_addresses") is not None:
        threat_white_list_payload["ipAddresses"] = threat_intelligence_allow_list.get(
            "ip_addresses"
        )
    return threat_white_list_payload


def convert_present_to_raw_dns(dns_settings: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        dns_settings(list(str)) : List of dns

    Returns:
        Dns list payload(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    dns_payload = {}
    if dns_settings.get("proxy_enabled") is not None:
        dns_payload["enableProxy"] = dns_settings.get("proxy_enabled")
    if dns_settings.get("servers") is not None:
        dns_payload["servers"] = dns_settings.get("servers")
    return dns_payload


def update_fire_policies_payload(
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
