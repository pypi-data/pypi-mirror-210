import copy
from typing import Any
from typing import Dict
from typing import List


def convert_raw_virtual_network_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    virtual_network_name: str,
    resource_id: str,
    subscription_id: str,
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
        resource_id: Azure Virtual Network resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "virtual_network_name": virtual_network_name,
        "location": resource["location"],
        "subscription_id": subscription_id,
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    properties = resource.get("properties")
    if properties:
        properties_parameters = {
            "bgpCommunities": "bgp_communities",
            "flowTimeoutInMinutes": "flow_timeout_in_minutes",
            "provisioningState": "provisioning_state",
        }
        for parameter_raw, parameter_present in properties_parameters.items():
            if parameter_raw in properties:
                resource_translated[parameter_present] = properties.get(parameter_raw)
        resource_translated["address_space"] = properties["addressSpace"][
            "addressPrefixes"
        ]
        if properties.get("subnets") is not None:
            existing_subnets_required_payload = convert_raw_to_present_vn_subnet(
                subnets=properties["subnets"]
            )
            resource_translated["subnets"] = existing_subnets_required_payload
    return resource_translated


def convert_present_to_raw_virtual_network(
    hub,
    subscription_id: str,
    address_space: List,
    location: str,
    bgp_communities: str = None,
    flow_timeout_in_minutes: int = None,
    subnets: List = None,
    tags: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        subscription_id: subscription id
        address_space: An array of IP address ranges that can be used by subnets of the virtual network.
        location: Resource location. Update this field will result in resource re-creation.
        bgp_communities: Bgp Communities sent over ExpressRoute with each route corresponding to a prefix in this VNET.
        flow_timeout_in_minutes: The FlowTimeout value (in minutes) for the Virtual Network
        subnets(list[dict], optional): List of Subnet in a virtual network resource.Each Subnet will have fields
          name(str, required), address_space(str, required) , security_group_id(str, optional) and service_endpoints(list, optional)
        tags: Resource tags.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "location": location,
        "properties": {"addressSpace": {"addressPrefixes": address_space}},
    }
    if tags is not None:
        payload["tags"] = tags
    if bgp_communities is not None:
        payload["properties"]["bgpCommunities"] = bgp_communities
    if flow_timeout_in_minutes is not None:
        payload["properties"]["flowTimeoutInMinutes"] = flow_timeout_in_minutes
    if subnets is not None:
        subnets_payload = convert_present_to_raw_vn_subnet(
            subscription_id=subscription_id, subnets=subnets
        )
        payload["properties"]["subnets"] = subnets_payload
    return payload


def update_virtual_network_payload(
    hub,
    subscription_id: str,
    existing_payload: Dict[str, Any],
    new_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
     PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        subscription_id: subscription id required to update network security group for VN subnet
        existing_payload: An existing resource state from Azure. This is usually a GET operation response.
        new_values: A dictionary of desired state values. If any property's value is None,
         this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
         do an update.

    Returns:
        A result dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    is_updated = False
    new_payload = copy.deepcopy(existing_payload)
    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        is_updated = True
    existing_properties = existing_payload["properties"]
    if (new_values.get("address_space") is not None) and (
        set(new_values["address_space"])
        != set(existing_properties["addressSpace"]["addressPrefixes"])
    ):
        new_payload["properties"]["addressSpace"]["addressPrefixes"] = new_values[
            "address_space"
        ]
        is_updated = True
    if (new_values.get("bgp_communities") is not None) and (
        new_values["bgp_communities"] != existing_properties.get("bgpCommunities")
    ):
        new_payload["properties"]["bgpCommunities"] = new_values.get("bgp_communities")
        is_updated = True
    if (new_values.get("flow_timeout_in_minutes") is not None) and (
        new_values["flow_timeout_in_minutes"]
        != existing_properties.get("flowTimeoutInMinutes")
    ):
        new_payload["properties"]["flowTimeoutInMinutes"] = new_values.get(
            "flow_timeout_in_minutes"
        )
        is_updated = True
    if new_values.get("subnets") is not None:
        existing_subnets = existing_properties.get("subnets")
        existing_subnets_required_payload = convert_raw_to_present_vn_subnet(
            subnets=existing_subnets
        )
        if diff_virtual_network_subnets(
            new_values.get("subnets"), existing_subnets_required_payload, "name"
        ):
            new_payload["properties"]["subnets"] = convert_present_to_raw_vn_subnet(
                subscription_id=subscription_id, subnets=new_values.get("subnets")
            )
            is_updated = True
    if is_updated:
        result["ret"] = new_payload
    return result


def convert_present_to_raw_vn_subnet(
    subscription_id: str, subnets: List[Dict[str, Any]]
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        subscription_id : subscription id to create network security group id
        subnets(list[dict], optional): List of Subnet in a virtual network resource.Each Subnet will have fields
        ((name(str), required), (address_space(str, required) and service_endpoints(list), optional))

    Returns:
        Subnets List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    raw_subnets: List = []
    for subnet in subnets:
        payload = {
            "name": subnet["name"],
            "properties": {"addressPrefix": subnet["address_prefix"]},
        }
        if subnet.get("security_group_id") is not None:
            payload["properties"]["networkSecurityGroup"] = {
                "id": subnet["security_group_id"]
            }
        if subnet.get("service_endpoints") is not None:
            services: List = []
            for endpoint in subnet.get("service_endpoints"):
                services.append({"service": endpoint})
            payload["properties"]["serviceEndpoints"] = services
        raw_subnets.append(payload)
    return raw_subnets


def convert_raw_to_present_vn_subnet(subnets: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        subnets(list[dict], optional): Resource List of Subnet in a virtual network resource.

    Returns:
         A subnet List that contains the parameters that match respective present function's input format.
    """
    present_subnets: List = []
    for subnet in subnets:
        new_subnet_payload = {
            "name": subnet.get("name"),
            "address_prefix": subnet["properties"]["addressPrefix"],
        }
        if subnet["properties"].get("networkSecurityGroup") is not None:
            new_subnet_payload["security_group_id"] = subnet["properties"][
                "networkSecurityGroup"
            ].get("id")
        if subnet["properties"].get("serviceEndpoints") is not None:
            services: List = []
            for endpoint in subnet["properties"]["serviceEndpoints"]:
                services.append(endpoint["service"])
            new_subnet_payload["service_endpoints"] = services
        present_subnets.append(new_subnet_payload)
    return present_subnets


def diff_virtual_network_subnets(
    new_values: List[Dict[str, any]],
    resource: List[Dict[str, any]],
    sorting_key: str,
):
    """
    Compares virtual network subnets to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        hub: The redistributed pop central hub.
        new_values: (List[Dict[str, any]]) Present value which will be given as input
        resource: (List[Dict[str, any]]) Raw resource response which needs to be compared with new_values
        sorting_key: (str) Primary/Unique key name within each dictionary , which will be used to sort dictionary
         objects with given list before comparing.

    Returns:
        A boolean value, True if there is any difference between List[Dict] arguments else returns False
    """
    for entry in new_values:
        for key, value in entry.items():
            if isinstance(entry[key], list):
                entry[key].sort()
    return sorted(new_values, key=lambda x: x[sorting_key]) != sorted(
        resource, key=lambda x: x[sorting_key]
    )
