import copy
from collections import OrderedDict
from typing import Any
from typing import Dict
from typing import List


def convert_raw_security_rules_to_present(
    hub, resource: Dict, idem_resource_name: str
) -> Dict[str, Any]:
    """
    Converts raw security_rules api response into present function format

    Args:
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_id = resource["id"]
    uri_parameters = OrderedDict(
        {
            "subscriptions": "subscription_id",
            "resourceGroups": "resource_group_name",
            "networkSecurityGroups": "network_security_group_name",
            "securityRules": "security_rule_name",
        }
    )
    uri_parameter_values = hub.tool.azure.uri.get_parameter_value_in_dict(
        resource_id, uri_parameters
    )
    translated_resource = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        **uri_parameter_values,
    }
    properties = resource.get("properties")
    properties_parameters = {
        "protocol": "protocol",
        "description": "description",
        "sourcePortRange": "source_port_range",
        "sourceAddressPrefix": "source_address_prefix",
        "destinationPortRange": "destination_port_range",
        "destinationAddressPrefix": "destination_address_prefix",
        "access": "access",
        "priority": "priority",
        "direction": "direction",
        "sourcePortRanges": "source_port_ranges",
        "destinationPortRanges": "destination_port_ranges",
        "sourceAddressPrefixes": "source_address_prefixes",
        "destinationAddressPrefixes": "destination_address_prefixes",
        "sourceApplicationSecurityGroups": "source_application_security_groups",
        "destinationApplicationSecurityGroups": "destination_application_security_groups",
    }
    for parameter_raw, parameter_present in properties_parameters.items():
        if properties.get(parameter_raw):
            if (
                parameter_present == "destination_application_security_groups"
                or parameter_present == "source_application_security_groups"
            ):
                translated_resource[parameter_present] = [
                    value["id"] for value in properties.get(parameter_raw)
                ]
            else:
                translated_resource[parameter_present] = properties.get(parameter_raw)
    return translated_resource


def convert_present_to_raw_security_rules(
    hub,
    priority: int,
    direction: str,
    access: str,
    protocol: str,
    description: str,
    source_port_range: str = None,
    source_port_ranges: List = None,
    source_address_prefix: str = None,
    source_address_prefixes: List = None,
    source_application_security_groups: List = None,
    destination_port_range: str = None,
    destination_port_ranges: List = None,
    destination_address_prefix: str = None,
    destination_address_prefixes: List = None,
    destination_application_security_groups: List = None,
) -> Dict[str, Any]:
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        priority(int): The priority of the security rule. The value can be between 100 and 4096.The priority number must
            be unique for each rule in the collection. The lower the priority number, the higher the priority of the rule.
        direction(str): The direction of the rule. The direction specifies if rule will be evaluated on incoming or outgoing traffic.
        access(str): The network traffic is allowed or denied.
        protocol(str): Network protocol this rule applies to.
        description(str, Optional): A description for this rule.
        source_port_range(str, Optional): The source port or range. Integer or range between 0 and 65535. Asterisk '*'
            can also be used to match all ports.
        source_port_ranges(List, Optional): The source port ranges. Either this or source_port_range need to be provided.
        source_address_prefix(str, Optional): The source address prefix. CIDR or source IP range. Asterisk '*' can also be used to match all
            source IPs. Default tags such as 'VirtualNetwork', 'AzureLoadBalancer' and 'Internet' can also be used. If
            this is an ingress rule, specifies where network traffic originates from.
        source_address_prefixes(List, Optional): The CIDR or source IP ranges.
        source_application_security_groups(List, Optional): The list of resource id of the application security group.
            Either one of source_address_prefix, source_address_prefixes or source_application_security_groups needs to be provided.
        destination_port_range(str, Optional): The destination port or range. Integer or range between 0 and 65535.
            Asterisk '*' can also be used to match all ports.
        destination_port_ranges(List, Optional): The destination port ranges. Either this or destination_port_range need to be provided.
        destination_address_prefix(str, Optional): The destination address prefix. CIDR or destination IP range.
            Asterisk '*' can also be used to match all source IPs. Default tags such as 'VirtualNetwork',
            'AzureLoadBalancer' and 'Internet' can also be used.
        destination_address_prefixes(List, Optional): The destination address prefixes. CIDR or destination IP ranges.
        destination_application_security_groups(List, Optional): The list of resource id of the application security group.
            Either one of destination_address_prefix, destination_address_prefixes or destination_application_security_groups needs to be provided.



    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"properties": {}}
    properties_parameters = {
        "protocol": "protocol",
        "description": "description",
        "sourcePortRange": "source_port_range",
        "sourceAddressPrefix": "source_address_prefix",
        "destinationPortRange": "destination_port_range",
        "destinationAddressPrefix": "destination_address_prefix",
        "access": "access",
        "priority": "priority",
        "direction": "direction",
        "sourcePortRanges": "source_port_ranges",
        "destinationPortRanges": "destination_port_ranges",
        "sourceAddressPrefixes": "source_address_prefixes",
        "destinationAddressPrefixes": "destination_address_prefixes",
        "sourceApplicationSecurityGroups": "source_application_security_groups",
        "destinationApplicationSecurityGroups": "destination_application_security_groups",
    }
    for parameter_raw, parameter_present in properties_parameters.items():
        if locals()[parameter_present]:
            if (
                parameter_present == "destination_application_security_groups"
                or parameter_present == "source_application_security_groups"
            ):
                payload["properties"][parameter_raw] = []
                for value in locals()[parameter_present]:
                    payload["properties"][parameter_raw].append({"id": value})
            else:
                payload["properties"][parameter_raw] = locals()[parameter_present]
    return payload


def update_security_rules_payload(
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
    properties_parameters = {
        "protocol": "protocol",
        "description": "description",
        "sourcePortRange": "source_port_range",
        "sourceAddressPrefix": "source_address_prefix",
        "destinationPortRange": "destination_port_range",
        "destinationAddressPrefix": "destination_address_prefix",
        "access": "access",
        "priority": "priority",
        "direction": "direction",
        "sourcePortRanges": "source_port_ranges",
        "destinationPortRanges": "destination_port_ranges",
        "sourceAddressPrefixes": "source_address_prefixes",
        "destinationAddressPrefixes": "destination_address_prefixes",
        "sourceApplicationSecurityGroups": "source_application_security_groups",
        "destinationApplicationSecurityGroups": "destination_application_security_groups",
    }
    optional_params = [
        "sourcePortRange",
        "sourceAddressPrefix",
        "destinationPortRange",
        "destinationAddressPrefix",
        "sourcePortRanges",
        "destinationPortRanges",
        "sourceAddressPrefixes",
        "destinationAddressPrefixes",
        "sourceApplicationSecurityGroups",
        "destinationApplicationSecurityGroups",
    ]

    for param in optional_params:
        new_payload["properties"].pop(param, None)

    for parameter_raw, parameter_present in properties_parameters.items():
        if new_values.get(parameter_present):
            if parameter_present in [
                "destination_application_security_groups",
                "source_application_security_groups",
            ]:
                if existing_properties.get(parameter_raw) and (
                    sorted(new_values.get(parameter_present))
                    == sorted(
                        [
                            value["id"]
                            for value in existing_properties.get(parameter_raw)
                        ]
                    )
                ):
                    new_payload["properties"][parameter_raw] = existing_properties.get(
                        parameter_raw
                    )
                else:
                    new_payload["properties"][parameter_raw] = []
                    for value in new_values.get(parameter_present):
                        new_payload["properties"][parameter_raw].append({"id": value})
                    need_update = True
            elif isinstance(new_values.get(parameter_present), List):
                if existing_properties.get(parameter_raw) and (
                    sorted(new_values.get(parameter_present))
                    == sorted(existing_properties.get(parameter_raw))
                ):
                    new_payload["properties"][parameter_raw] = existing_properties.get(
                        parameter_raw
                    )
                else:
                    new_payload["properties"][parameter_raw] = new_values.get(
                        parameter_present
                    )
                    need_update = True
            else:
                if new_values.get(parameter_present) != existing_properties.get(
                    parameter_raw
                ):
                    new_payload["properties"][parameter_raw] = new_values.get(
                        parameter_present
                    )
                    need_update = True
                else:
                    new_payload["properties"][parameter_raw] = existing_properties.get(
                        parameter_raw
                    )

    if need_update:
        result["ret"] = new_payload
    return result
