"""State module for managing network Security Rules."""
import copy
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    network_security_group_name: str,
    security_rule_name: str,
    priority: int,
    direction: str,
    access: str,
    protocol: str,
    description: str = None,
    source_port_range: str = None,
    source_port_ranges: List[str] = None,
    source_address_prefix: str = None,
    source_address_prefixes: List[str] = None,
    source_application_security_groups: List[str] = None,
    destination_port_range: str = None,
    destination_port_ranges: List[str] = None,
    destination_address_prefix: str = None,
    destination_address_prefixes: List[str] = None,
    destination_application_security_groups: List[str] = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict[str, Any]:
    r"""Create or update Security Rules.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        network_security_group_name(str): The name of the network security group.
        security_rule_name(str): The name of the security rule.
        priority(int): The priority of the security rule. The value can be between 100 and 4096.The priority number must
            be unique for each rule in the collection. The lower the priority number, the higher the priority of the rule.
        direction(str): The direction of the rule. The direction specifies if rule will be evaluated on incoming or outgoing traffic.
        access(str): The network traffic is allowed or denied.
        protocol(str): Network protocol this rule applies to.
        description(str, Optional): A description for this rule.
        source_port_range(str, Optional): The source port or range. Integer or range between 0 and 65535. Asterisk '*'
            can also be used to match all ports.
        source_port_ranges(list[str], Optional): The source port ranges. Either this or source_port_range need to be provided.
        source_address_prefix(str, Optional): The source address prefix. CIDR or source IP range. Asterisk '*' can also be used to match all
            source IPs. Default tags such as 'VirtualNetwork', 'AzureLoadBalancer' and 'Internet' can also be used. If
            this is an ingress rule, specifies where network traffic originates from.
        source_address_prefixes(list[str], Optional): The CIDR or source IP ranges.
        source_application_security_groups(list[str], Optional): The list of resource id of the application security group.
            Either one of source_address_prefix, source_address_prefixes or source_application_security_groups needs to be provided.
        destination_port_range(str, Optional): The destination port or range. Integer or range between 0 and 65535.
            Asterisk '*' can also be used to match all ports.
        destination_port_ranges(list[str], Optional): The destination port ranges. Either this or destination_port_range need to be provided.
        destination_address_prefix(str, Optional): The destination address prefix. CIDR or destination IP range.
            Asterisk '*' can also be used to match all source IPs. Default tags such as 'VirtualNetwork',
            'AzureLoadBalancer' and 'Internet' can also be used.
        destination_address_prefixes(list[str], Optional): The destination address prefixes. CIDR or destination IP ranges.
        destination_application_security_groups(list[str], Optional): The list of resource id of the application security group.
            Either one of destination_address_prefix, destination_address_prefixes or destination_application_security_groups needs to be provided.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Security rule resource id.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.security_rules.present:
                - name: rule1
                - resource_id: /subscriptions/12345678-1234-1234-1234-aaabc1234aaa/resourceGroups/rg-1/providers/Microsoft.Network/networkSecurityGroups/nsg-1/securityRules/rule1
                - resource_group_name: rg-1
                - subscription_id: 12345678-1234-1234-1234-aaabc1234aaa
                - network_security_group_name: nsg-1
                - security_rule_name: rule1
                - protocol: '*'
                - source_address_prefix: '*'
                - destination_port_range: '80'
                - destination_address_prefix: '*'
                - access: Allow
                - priority: 130
                - direction: Inbound
                - source_port_ranges:
                  - '20'
                  - '50'
                  - '80'
    """
    result = {
        "name": name,
        "result": True,
        "old_state": None,
        "new_state": None,
        "comment": [],
    }
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id

    if resource_id is None:
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkSecurityGroups/{network_security_group_name}/securityRules/{security_rule_name}"

    response_get = await hub.exec.azure.network.security_rules.get(
        ctx, resource_id=resource_id, raw=True
    )

    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.network.security_rules {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if not response_get["ret"]:
        if ctx.get("test", False):
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_group_name": resource_group_name,
                    "network_security_group_name": network_security_group_name,
                    "security_rule_name": security_rule_name,
                    "priority": priority,
                    "direction": direction,
                    "access": access,
                    "protocol": protocol,
                    "description": description,
                    "source_port_range": source_port_range,
                    "source_port_ranges": source_port_ranges,
                    "source_address_prefix": source_address_prefix,
                    "source_address_prefixes": source_address_prefixes,
                    "source_application_security_groups": source_application_security_groups,
                    "destination_port_range": destination_port_range,
                    "destination_port_ranges": destination_port_ranges,
                    "destination_address_prefix": destination_address_prefix,
                    "destination_address_prefixes": destination_address_prefixes,
                    "destination_application_security_groups": destination_application_security_groups,
                    "subscription_id": subscription_id,
                    "resource_id": resource_id,
                },
            )
            result["comment"].append(
                f"Would create azure.network.security_rules '{name}'"
            )
            return result

        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.network.security_rules.convert_present_to_raw_security_rules(
                priority=priority,
                direction=direction,
                access=access,
                protocol=protocol,
                description=description,
                source_port_range=source_port_range,
                source_port_ranges=source_port_ranges,
                source_address_prefix=source_address_prefix,
                source_address_prefixes=source_address_prefixes,
                source_application_security_groups=source_application_security_groups,
                destination_port_range=destination_port_range,
                destination_port_ranges=destination_port_ranges,
                destination_address_prefix=destination_address_prefix,
                destination_address_prefixes=destination_address_prefixes,
                destination_application_security_groups=destination_application_security_groups,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{hub.exec.azure.URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkSecurityGroups/{network_security_group_name}/securityRules/{security_rule_name}?api-version=2022-07-01",
                success_codes=[200, 201],
                json=payload,
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.network.security_rules {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.security_rules.convert_raw_security_rules_to_present(
                resource=response_put["ret"], idem_resource_name=name
            )
            result["comment"].append(f"Created azure.network.security_rules '{name}'")
            return result
    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.network.security_rules.convert_raw_security_rules_to_present(
            resource=existing_resource, idem_resource_name=name
        )
        # Generate a new PUT operation payload with new values
        new_payload = hub.tool.azure.network.security_rules.update_security_rules_payload(
            response_get["ret"],
            {
                "priority": priority,
                "direction": direction,
                "access": access,
                "protocol": protocol,
                "description": description,
                "source_port_range": source_port_range,
                "source_port_ranges": source_port_ranges,
                "source_address_prefix": source_address_prefix,
                "source_address_prefixes": source_address_prefixes,
                "source_application_security_groups": source_application_security_groups,
                "destination_port_range": destination_port_range,
                "destination_port_ranges": destination_port_ranges,
                "destination_address_prefix": destination_address_prefix,
                "destination_address_prefixes": destination_address_prefixes,
                "destination_application_security_groups": destination_application_security_groups,
            },
        )
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.network.security_rules '{name}' has no property need to be updated."
            )
            return result
        else:
            if ctx.get("test", False):
                result[
                    "new_state"
                ] = hub.tool.azure.network.security_rules.convert_raw_security_rules_to_present(
                    resource=new_payload["ret"], idem_resource_name=name
                )
                result["comment"].append(
                    f"Would update azure.network.security_rules '{name}'"
                )
                return result
            else:
                # PUT call to update the resource
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{hub.exec.azure.URL}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkSecurityGroups/{network_security_group_name}/securityRules/{security_rule_name}?api-version=2022-07-01",
                    success_codes=[200, 201],
                    json=new_payload["ret"],
                )

                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not update azure.network.security_rules {response_put['comment']} {response_put['ret']}"
                    )
                    result["result"] = False
                    result["comment"] = [
                        response_put["comment"],
                        response_put["ret"],
                    ]
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.security_rules.convert_raw_security_rules_to_present(
                    resource=response_put["ret"], idem_resource_name=name
                )
                result["comment"].append(
                    f"Updated azure.network.security_rules '{name}'"
                )
                return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    network_security_group_name: str,
    security_rule_name: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    r"""Delete Security Rule.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        network_security_group_name(str): The name of the network security group.
        security_rule_name(str): The name of the security rule.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.security_rules.absent:
                - name: value
                - resource_group_name: value
                - network_security_group_name: value
                - security_rule_name: value
    """
    result = dict(name=name, result=True, comment=[], old_state=None, new_state=None)
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkSecurityGroups/{network_security_group_name}/securityRules/{security_rule_name}"

    response_get = await hub.exec.azure.network.security_rules.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.network.security_rules {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name
        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.network.security_rules '{name}'"
            )
            return result

        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{hub.exec.azure.URL}{resource_id}?api-version=2022-07-01",
            success_codes=[200, 202, 204],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.network.security_rules {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(f"Deleted azure.network.security_rules '{name}'")
        return result

    else:
        # If Azure returns 'Not Found' error, it means the resource is absent.
        result["comment"].append(
            f"azure.network.security_rules '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Security Rules under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.security_rules
    """
    result = {}
    ret_list = await hub.exec.azure.network.security_rules.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe network security_rules {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.security_rules.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
