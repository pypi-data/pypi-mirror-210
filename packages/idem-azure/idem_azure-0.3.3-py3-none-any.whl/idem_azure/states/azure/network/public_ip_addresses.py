"""State module for managing Public IP Address."""
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
    public_ip_address_name: str,
    location: str,
    allocation_method: str,
    zones: List[str] = None,
    ddos_protection_mode: str = None,
    ddos_protection_plan_id: str = None,
    domain_name_label: str = None,
    edge_zone: str = None,
    idle_timeout_in_minutes: int = None,
    ip_tags: Dict[str, str] = None,
    ip_version: str = None,
    public_ip_prefix_id: str = None,
    reverse_fqdn: str = None,
    sku: str = None,
    sku_tier: str = None,
    tags: Dict[str, str] = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Public IP Addresses.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        public_ip_address_name(str): The name of the public IP address.
        location(str): Resource location.
        allocation_method(str): Defines the allocation method for this IP address.
        zones(list[str], Optional): A collection containing the availability zone to allocate the Public IP in.
        ddos_protection_mode(str, Optional): The DDoS protection mode of the public IP.
        ddos_protection_plan_id(str, Optional): The ID of DDoS protection plan associated with the public IP.
        domain_name_label(str, Optional): Label for the Domain Name.
        edge_zone(str, Optional): Specifies the Edge Zone within the Azure Region where this Public IP should exist.
        idle_timeout_in_minutes(int, Optional): Specifies the timeout for the TCP idle connection.
        ip_tags(dict, Optional): A mapping of IP tags to assign to the public IP.
        ip_version(str, Optional): The IP Version to use.
        public_ip_prefix_id(str, Optional): If specified then public IP address allocated will be provided from the public IP prefix resource.
        reverse_fqdn(str, Optional): A fully qualified domain name that resolves to this public IP address.
        sku(str, Optional): The SKU of the Public IP.
        sku_tier(str, Optional): The SKU Tier that should be used for the Public IP.
        tags(dict, Optional): Resource tags.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Management group resource id on Azure

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.public_ip_addresses.present:
                - name: value
                - resource_group_name: value
                - public_ip_address_name: value
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/publicIPAddresses/{public_ip_address_name}"

    response_get = await hub.exec.azure.network.public_ip_addresses.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if not response_get["ret"]:
            if ctx.get("test", False):
                # Return a proposed state by Idem state --test
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "public_ip_address_name": public_ip_address_name,
                        "location": location,
                        "allocation_method": allocation_method,
                        "zones": zones,
                        "ddos_protection_mode": ddos_protection_mode,
                        "ddos_protection_plan_id": ddos_protection_plan_id,
                        "domain_name_label": domain_name_label,
                        "edge_zone": edge_zone,
                        "idle_timeout_in_minutes": idle_timeout_in_minutes,
                        "ip_tags": ip_tags,
                        "ip_version": ip_version,
                        "public_ip_prefix_id": public_ip_prefix_id,
                        "reverse_fqdn": reverse_fqdn,
                        "sku": sku,
                        "sku_tier": sku_tier,
                        "tags": tags,
                        "resource_id": resource_id,
                        "subscription_id": subscription_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.network.public_ip_addresses '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.network.public_ip_addresses.convert_present_to_raw_public_ip_addresses(
                    location=location,
                    allocation_method=allocation_method,
                    zones=zones,
                    ddos_protection_mode=ddos_protection_mode,
                    ddos_protection_plan_id=ddos_protection_plan_id,
                    domain_name_label=domain_name_label,
                    edge_zone=edge_zone,
                    idle_timeout_in_minutes=idle_timeout_in_minutes,
                    ip_tags=ip_tags,
                    ip_version=ip_version,
                    public_ip_prefix_id=public_ip_prefix_id,
                    reverse_fqdn=reverse_fqdn,
                    sku=sku,
                    sku_tier=sku_tier,
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
                        f"Could not create azure.network.public_ip_addresses {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.public_ip_addresses.convert_raw_public_ip_addresses_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    public_ip_address_name=public_ip_address_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Created azure.network.public_ip_addresses '{name}'"
                )
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.public_ip_addresses.convert_raw_public_ip_addresses_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                public_ip_address_name=public_ip_address_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.network.public_ip_addresses.update_public_ip_addresses_payload(
                existing_resource,
                {
                    "allocation_method": allocation_method,
                    "zones": zones,
                    "ddos_protection_mode": ddos_protection_mode,
                    "ddos_protection_plan_id": ddos_protection_plan_id,
                    "domain_name_label": domain_name_label,
                    "edge_zone": edge_zone,
                    "idle_timeout_in_minutes": idle_timeout_in_minutes,
                    "ip_tags": ip_tags,
                    "ip_version": ip_version,
                    "public_ip_prefix_id": public_ip_prefix_id,
                    "reverse_fqdn": reverse_fqdn,
                    "sku": sku,
                    "sku_tier": sku_tier,
                    "tags": tags,
                },
            )

            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.public_ip_addresses '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.public_ip_addresses.convert_raw_public_ip_addresses_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        public_ip_address_name=public_ip_address_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.network.public_ip_addresses '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.public_ip_addresses '{name}' has no property need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.network.public_ip_addresses {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.public_ip_addresses.convert_raw_public_ip_addresses_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                public_ip_address_name=public_ip_address_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.network.public_ip_addresses '{name}' has no property need to be updated."
                )
                return result

            result["comment"].append(
                f"Updated azure.network.public_ip_addresses '{name}'"
            )
            return result

    else:
        hub.log.debug(
            f"Could not get azure.network.public_ip_addresses {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    public_ip_address_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete Public IP Addresses.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        public_ip_address_name(str): The name of the public IP address.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.public_ip_addresses.absent:
                - name: value
                - resource_group_name: value
                - public_ip_address_name: value
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
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/publicIPAddresses/{public_ip_address_name}"
    response_get = await hub.exec.azure.network.public_ip_addresses.get(
        ctx,
        resource_id=resource_id,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name

            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.network.public_ip_addresses '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200, 202, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.public_ip_addresses '{name}' {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.network.public_ip_addresses '{name}'"
            )
            return result

        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.network.public_ip_addresses '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.public_ip_addresses '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Public IP Addresses under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure_auto.network.public_ip_addresses
    """
    result = {}
    ret_list = await hub.exec.azure.network.public_ip_addresses.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe public ip addresses {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.public_ip_addresses.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
