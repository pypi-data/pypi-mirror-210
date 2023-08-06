"""State module for managing Network interface."""
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
    network_interface_name: str,
    location: str,
    ip_configurations: List[
        make_dataclass(
            "IpConfigurationsSet",
            [
                ("name", str, field(default=None)),
                ("private_ip_address_allocation", str, field(default=None)),
                ("subnet_id", str, field(default=None)),
                ("private_ip_address_version", str, field(default=None)),
                ("private_ip_address", str, field(default=None)),
                ("primary", bool, field(default=False)),
            ],
        )
    ],
    tags: Dict = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Network Interfaces.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        network_interface_name(str): The name of the network interface.
        location(str): Resource location. This field can not be updated.
        ip_configurations(list[dict[str, Any]]): A list of IPConfigurations of the network interface. Each ip configuration supports fields:

            * name(str):
                The name of the resource that is unique within a resource group.
            * private_ip_address_allocation(str):
                The allocation method used for the Private IP Address. Possible values are Dynamic and Static.
                Azure does not assign a Dynamic IP Address until the Network Interface is attached to a running Virtual Machine(or other resource).
            * subnet_id(str):
                Resource ID of the Subnet bound to the IP configuration. The name of the resource that is unique within a resource group.
                This is required when private_ip_address_version is set to IPv4.
            * private_ip_address_version(str):
                The specific IP configuration is IPv4 or IPv6. Default is IPv4.
            * private_ip_address(str):
                The Static IP Address which should be used. When private_ip_address_allocation is set to Static, private_ip_address can be configured.
            * primary(bool):
                To check if this is the primary IP Configuration. Must be true for the first ip_configuration when
                multiple are specified. Defaults to false. Primary attribute must be true for the first ip_configuration
                when multiple are specified. Defaults to false.
        tags(dict[str, str], Optional): Resource tags.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Network Interface resource id on Azure.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-nic:
              azure.network.network_interfaces.present:
                - name: my-nic
                - resource_group_name: my-rg
                - network_interface_name: my-nic
                - location: southindia
                - subscription_id: my-subscription
                - ip_configurations:
                  - name: my-ipc
                    private_ip_address_allocation: Static
                    subnet_id: subnet_name
                    private_ip_address_version: IPv4
                    private_ip_address: 10.0.0.24
                    primary: true
                - tags:
                    my-tag-key: my-tag-value

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
        resource_id = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
            f"/providers/Microsoft.Network/networkInterfaces/{network_interface_name}"
        )
    response_get = await hub.exec.azure.network.network_interfaces.get(
        ctx, resource_id=resource_id, raw=True
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
                        "subscription_id": subscription_id,
                        "network_interface_name": network_interface_name,
                        "location": location,
                        "ip_configurations": ip_configurations,
                        "tags": tags,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.network.network_interfaces '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.network.network_interfaces.convert_present_to_raw_network_interfaces(
                    location=location,
                    ip_configurations=ip_configurations,
                    tags=tags,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-08-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.network.network_interfaces"
                        f" '{name}' {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.network_interfaces.convert_raw_network_interfaces_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    subscription_id=subscription_id,
                    network_interface_name=network_interface_name,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Created azure.network.network_interfaces '{name}'"
                )
                return result
        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.network_interfaces.convert_raw_network_interfaces_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                subscription_id=subscription_id,
                network_interface_name=network_interface_name,
                resource_id=resource_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.network.network_interfaces.update_network_interfaces_payload(
                existing_resource,
                {
                    "ip_configurations": ip_configurations,
                    "tags": tags,
                },
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.network_interfaces '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.network_interfaces.convert_raw_network_interfaces_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        subscription_id=subscription_id,
                        network_interface_name=network_interface_name,
                        resource_id=resource_id,
                    )
                    result["comment"].append(
                        f"Would update azure.network.network_interfaces '{name}'"
                    )
                return result

                # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.network_interfaces '{name}' has no property need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-08-01",
                success_codes=[200, 201],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.network.network_interfaces "
                    f"{response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.network_interfaces.convert_raw_network_interfaces_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                subscription_id=subscription_id,
                network_interface_name=network_interface_name,
                resource_id=resource_id,
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.network.network_interfaces '{name}' has no property to be updated."
                )
                return result
            result["comment"].append(
                f"Updated azure.network.network_interfaces '{name}'"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.network_interfaces {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    network_interface_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete Network Interfaces.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        network_interface_name(str): The name of the network interface.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.network_interfaces.absent:
                - name: value
                - resource_group_name: value
                - network_interface_name: value
                - subscription_id: my-subscription
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
    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.Network/networkInterfaces/{network_interface_name}"
    )

    response_get = await hub.exec.azure.network.network_interfaces.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.network.network_interfaces.convert_raw_network_interfaces_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                subscription_id=subscription_id,
                network_interface_name=network_interface_name,
                resource_id=resource_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.network.network_interfaces '{name}'"
                )
                return result

            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-08-01",
                success_codes=[200, 202],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.network_interfaces {response_delete['comment']}"
                    f" {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.network.network_interfaces '{name}'"
            )
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.network.network_interfaces '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.network_interfaces '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Network Interfaces under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.network_interfaces
    """
    result = {}
    ret_list = await hub.exec.azure.network.network_interfaces.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe network_interfaces {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.network_interfaces.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
