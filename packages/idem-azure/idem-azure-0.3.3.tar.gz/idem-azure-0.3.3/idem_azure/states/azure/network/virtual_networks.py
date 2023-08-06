"""State module for managing Virtual Network."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List


__contracts__ = ["resource"]


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    virtual_network_name: str,
    address_space: List,
    location: str,
    resource_id: str = None,
    bgp_communities: Dict = None,
    flow_timeout_in_minutes: int = None,
    subnets: List[
        make_dataclass(
            "SubnetSet",
            [
                ("name", str, field(default=None)),
                ("address_prefix", str, field(default=None)),
                ("security_group_id", str, field(default=None)),
                ("service_endpoints", List, field(default=None)),
            ],
        )
    ] = None,
    subscription_id: str = None,
    tags: Dict = None,
) -> Dict:
    r"""Create or update Virtual Networks.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        address_space(list): An array of IP address ranges that can be used by subnets of the virtual network.
        location(str): Resource location. This field can not be updated.
        resource_id(str, Optional): Virtual Network resource id on Azure
        bgp_communities(dict, Optional): Bgp Communities sent over ExpressRoute with each route corresponding to a prefix in this VNET.
        flow_timeout_in_minutes(int, Optional): The FlowTimeout value (in minutes) for the Virtual Network
        subnets(list, Optional): List of Subnet in a virtual network resource.Each Subnet will have fields

            * name(str):
                The name of subnet.
            * address_space(str):
                Address space of the subnet.
            * security_group_id(str, Optional):
                The security group id.
            * service_endpoints(list, Optional):
                List of service endpoint.
        subscription_id(str, Optional): Subscription Unique id.
        tags(dict, Optional): Resource tags.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            my-vnet:
              azure.network.virtual_networks.present:
                - name: my-vnet
                - resource_group_name: my-rg-1
                - virtual_network_name: my-vnet-1
                - location: westus
                - flow_timeout_in_minutes: 15
                - tags:
                    my-tag-key: my-tag-value
                - subnets:
                    - name: subnet_name
                      address_prefix: 10.0.0.0/26
                      security_group_id: /subscriptions/subscription_id/resourceGroups/resource_group_name/providers/Microsoft.Network/networkSecurityGroups/network-security-group-name
                      service_endpoints:
                          - Microsoft.Storage
                - address_space:
                    - 10.0.0.0/26
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}"
    response_get = await hub.exec.azure.network.virtual_networks.get(
        ctx,
        resource_id=resource_id,
        raw=True,
    )
    if response_get["result"]:
        if response_get["ret"] is None:
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "virtual_network_name": virtual_network_name,
                        "address_space": address_space,
                        "tags": tags,
                        "location": location,
                        "resource_id": resource_id,
                        "flow_timeout_in_minutes": flow_timeout_in_minutes,
                        "bgp_communities": bgp_communities,
                        "subnets": subnets,
                        "subscription_id": subscription_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.network.virtual_networks '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.network.virtual_networks.convert_present_to_raw_virtual_network(
                    subscription_id=subscription_id,
                    address_space=address_space,
                    location=location,
                    bgp_communities=bgp_communities,
                    flow_timeout_in_minutes=flow_timeout_in_minutes,
                    subnets=subnets,
                    tags=tags,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                    success_codes=[200, 201],
                    json=payload,
                )

                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.network.virtual_networks {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    virtual_network_name=virtual_network_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Created azure.network.virtual_networks '{name}'"
                )
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = (
                hub.tool.azure.network.virtual_networks.update_virtual_network_payload(
                    subscription_id,
                    existing_resource,
                    {
                        "address_space": address_space,
                        "bgp_communities": bgp_communities,
                        "flow_timeout_in_minutes": flow_timeout_in_minutes,
                        "subnets": subnets,
                        "tags": tags,
                    },
                )
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.virtual_networks '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        virtual_network_name=virtual_network_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.network.virtual_networks '{name}'"
                    )
                return result
            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.virtual_networks '{name}' has no property need to be updated."
                )
                return result
            result["comment"] += new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200],
                json=new_payload["ret"],
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.network.virtual_networks {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Updated azure.network.virtual_networks '{name}'")
            return result

    else:
        hub.log.debug(
            f"Could not get azure.network.virtual_networks {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    virtual_network_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete Virtual Networks.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.virtual_networks.absent:
                - name: value
                - resource_group_name: value
                - virtual_network_name: value
    """
    result = dict(name=name, result=True, comment=[], old_state=None, new_state=None)
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}"
    response_get = await hub.exec.azure.network.virtual_networks.get(
        ctx,
        resource_id=resource_id,
        raw=True,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.network.virtual_networks.convert_raw_virtual_network_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.network.virtual_networks '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200, 202, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.virtual_networks '{name}' {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(f"Deleted azure.network.virtual_networks '{name}'")
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.network.virtual_networks '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.virtual_networks '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Virtual Networks under the same subscription

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.virtual_networks
    """
    result = {}
    ret_list = await hub.exec.azure.network.virtual_networks.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe network virtual_networks {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.virtual_networks.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
