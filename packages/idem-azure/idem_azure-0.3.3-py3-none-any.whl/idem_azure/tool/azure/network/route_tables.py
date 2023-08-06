import copy
from typing import Any
from typing import Dict
from typing import List


def update_route_table_payload(
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
    if (new_values.get("disable_bgp_route_propagation") is not None) and (
        new_values["disable_bgp_route_propagation"]
        != existing_properties.get("disableBgpRoutePropagation")
    ):
        new_payload["properties"]["disableBgpRoutePropagation"] = new_values[
            "disable_bgp_route_propagation"
        ]
        need_update = True
    if (new_values.get("tags") is not None) and (
        new_values["tags"] != existing_payload.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        need_update = True
    if new_values["routes"] is not None:
        if len(existing_properties.get("routes")) == 0 or compare_routes(
            new_values["routes"],
            convert_raw_routes_to_present(existing_properties.get("routes")),
            "route_name",
        ):
            new_payload["properties"]["routes"] = convert_present_to_raw_routes(
                new_values["routes"]
            )
            need_update = True
    if need_update:
        result["ret"] = new_payload
    return result


def convert_raw_route_tables_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    route_table_name: str,
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
        resource_id: Azure Subnet resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "route_table_name": route_table_name,
        "location": resource["location"],
        "subscription_id": subscription_id,
    }
    if resource.get("tags") is not None:
        resource_translated["tags"] = resource["tags"]
    properties = resource.get("properties")
    if properties:
        if properties.get("disableBgpRoutePropagation") is not None:
            resource_translated["disable_bgp_route_propagation"] = properties.get(
                "disableBgpRoutePropagation"
            )
        if len(properties.get("routes")) != 0:
            resource_translated["routes"] = convert_raw_routes_to_present(
                properties.get("routes")
            )
    return resource_translated


def convert_present_to_raw_route_tables(
    hub,
    location: str,
    disable_bgp_route_propagation: bool = None,
    routes: List = None,
    tags: str = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location: Resource location. This field can not be updated.
        disable_bgp_route_propagation:  Whether to disable the routes learned by BGP on that route table. True means disable.
        routes: An array of routes on the route table. Collection of routes contained within a route table.
         Defaults to None
         * route_name(str) -- The name of the resource that is unique within a resource group.
         * address_prefix(str) -- The destination CIDR to which the route applies.
         * next_hop_type(str) -- The type of Azure hop the packet should be sent to.
         * next_hop_ip_address(str, optional) -- The IP address packets should be forwarded to. Next hop values are only allowed in routes where the next hop type is VirtualAppliance.
        tags: Resource tags.
    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": dict()}
    if tags is not None:
        payload["tags"] = tags
    if disable_bgp_route_propagation is not None:
        payload["properties"][
            "disableBgpRoutePropagation"
        ] = disable_bgp_route_propagation
    if routes is not None:
        payload["properties"]["routes"] = convert_present_to_raw_routes(routes)
    return payload


def convert_present_to_raw_routes(routes: List):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        routes(list[dict], required): List of Route in a route table resource.Each Route will have fields
        ((route_name(str), required), (address_prefix(str), required), (next_hop_type(str), required) and (next_hop_ip_address(str), optional))

    Returns:
        Routes List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    raw_routes: List = []
    for route in routes:
        new_route_payload = {
            "name": route["route_name"],
            "properties": {
                "addressPrefix": route["address_prefix"],
                "nextHopType": route["next_hop_type"],
            },
        }
        if route.get("next_hop_ip_address") is not None:
            new_route_payload["properties"]["nextHopIpAddress"] = route[
                "next_hop_ip_address"
            ]
        raw_routes.append(new_route_payload)
    return raw_routes


def convert_raw_routes_to_present(routes: List):
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
    present input parameters.

    Args:
        routes(list[dict], optional): Resource List of Routes in a Route Table resource.

    Returns:
         A route List that contains the parameters that match respective present function's input format.
    """
    present_routes: List = []
    for route in routes:
        new_route_payload = {
            "route_name": route["name"],
            "address_prefix": route["properties"]["addressPrefix"],
            "next_hop_type": route["properties"]["nextHopType"],
        }
        if route.get("properties").get("nextHopIpAddress") is not None:
            new_route_payload["next_hop_ip_address"] = route["properties"][
                "nextHopIpAddress"
            ]
        present_routes.append(new_route_payload)
    return present_routes


def compare_routes(
    new_values: List[Dict[str, any]], resource: List[Dict[str, any]], sorting_key: str
):
    """
    Compares routes to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        new_values: (List[Dict[str, any]]) Present value which will be given as input
        resource: (List[Dict[str, any]]) Raw resource response which needs to be compared with new_values
        sorting_key: (str) Primary/Unique key name within each dictionary , which will be used to sort dictionary
         objects with given list before comparing.

    Returns:
        A boolean value, True if there is any difference between List[Dict] arguments else returns False
    """
    if len(new_values) == 0 or len(resource) == 0:
        return True
    return sorted(new_values, key=lambda x: x[sorting_key]) != sorted(
        resource, key=lambda x: x[sorting_key]
    )
