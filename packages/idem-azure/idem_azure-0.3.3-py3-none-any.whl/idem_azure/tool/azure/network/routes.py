import copy
from typing import Any
from typing import Dict


def update_route_payload(
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
        new_payload["properties"]["addressPrefix"] = new_values["address_prefix"]
        need_update = True
    if (new_values.get("next_hop_type") is not None) and (
        new_values["next_hop_type"] != existing_properties.get("nextHopType")
    ):
        new_payload["properties"]["nextHopType"] = new_values["next_hop_type"]
        need_update = True
    if new_values.get("next_hop_ip_address") != existing_properties.get(
        "nextHopIpAddress"
    ):
        new_payload["properties"]["nextHopIpAddress"] = new_values.get(
            "next_hop_ip_address"
        )
        need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_routes_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    route_table_name: str,
    route_name: str,
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
        route_table_name: Azure Route Table resource name.
        route_name: Azure Route resource name.
        resource_id: Azure Route resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "route_name": route_name,
        "route_table_name": route_table_name,
        "subscription_id": subscription_id,
    }
    properties = resource.get("properties")
    if properties:
        resource_translated["address_prefix"] = properties.get("addressPrefix")
        resource_translated["next_hop_type"] = properties.get("nextHopType")
        if properties.get("nextHopIpAddress") is not None:
            resource_translated["next_hop_ip_address"] = properties.get(
                "nextHopIpAddress"
            )

    return resource_translated


def convert_present_to_raw_routes(
    hub,
    address_prefix: str,
    next_hop_type: str,
    next_hop_ip_address: str = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        address_prefix(str) : The destination CIDR to which the route applies.
        next_hop_type(str) : The type of Azure hop the packet should be sent to.
        next_hop_ip_address(str, optional) : The IP address packets should be forwarded to. Next hop values are only allowed in routes where the next hop type is VirtualAppliance.
    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "properties": {"addressPrefix": address_prefix, "nextHopType": next_hop_type}
    }
    if next_hop_ip_address is not None:
        payload["properties"]["nextHopIpAddress"] = next_hop_ip_address
    return payload
