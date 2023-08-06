"""States module for managing Firewall."""
import copy
from dataclasses import field
from dataclasses import make_dataclass
from typing import Any
from typing import Dict
from typing import List

__contracts__ = ["resource"]
__reconcile_wait__ = {"static": {"wait_in_seconds": 20}}


async def present(
    hub,
    ctx,
    name: str,
    location: str,
    resource_group_name: str,
    firewall_name: str,
    subscription_id: str = None,
    tags: Dict = None,
    resource_id: str = None,
    zones: List[str] = None,
    sku: make_dataclass(
        "sku",
        [("name", str, field(default=None)), ("tier", str, field(default=None))],
    ) = None,
    firewall_policy_id: str = None,
    ip_configuration: List[
        make_dataclass(
            "ipConfiguration",
            [
                ("name", str, field(default=None)),
                ("subnet_id", str, field(default=None)),
                ("public_ip_address_id", str, field(default=None)),
            ],
        )
    ] = None,
    management_ip_configuration: make_dataclass(
        "managementIpConfiguration",
        [
            ("name", str, field(default=None)),
            ("subnet_id", str, field(default=None)),
            ("public_ip_address_id", str, field(default=None)),
        ],
    ) = None,
) -> Dict:
    r"""Create or update firewall.

    Args:
        name(str): The identifier for this state.
        location(str): Resource location. Changing this forces a new resource to be created.
        resource_group_name(str): The name of the resource group.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): firewall resource id on Azure
        tags(dict[str, str], Optional): Resource tags.
        firewall_name(str): The name of the firewall.
        zones(list[str]): A list of availability zones denoting where the resource needs to come from.
        sku(dict[str, Any], Optional): The SKU of the Firewall.

            * name(str):
                SKU name of the Firewall. Possible values are AZFW_Hub and AZFW_VNet. Changing this forces a new resource to be created.
            * tier(str):
                SKU tier of the Firewall. Possible values are Premium, Standard and Basic.
        firewall_policy_id(str): The ID of the Firewall Policy applied to this Firewall.
        ip_configuration(list[dict[str, Any]], Optional): IP configuration of the Firewall.

            * name(str):
                SKU name of the Firewall. Possible values are AZFW_Hub and AZFW_VNet. Changing this forces a new resource to be created.
            * subnet_id(str):
                SKU tier of the Firewall. Possible values are Premium, Standard and Basic.
            * public_ip_address_id(str):
                SKU tier of the Firewall. Possible values are Premium, Standard and Basic.
        management_ip_configuration(dict[str, Any], Optional): Management IP configuration of the Firewall.

            * name(str):
                Specifies the name of the IP Configuration.
            * subnet_id(str):
                Reference to the subnet associated with the IP Configuration. Changing this forces a new resource to be created.
            * public_ip_address_id(str):
                The ID of the Public IP Address associated with the firewall.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.firewall.present:
                - name: my_firewall
                - subscription_id: my_sub_id
                - resource_group_name: my_rg-1
                - firewall_name: my-firewall
                - location: eastus
                - tags:
                    key: valuer
                - zones:
                    - 1
                - sku:
                    name: AZFW_VNet
                    tier: Premium
                - firewall_policy_id: my_fp_id
                - ip_configuration:
                    - name: name
                      subnet_id: my_sub_id
                      public_ip_address_id: my_public_ip_address
                - management_ip_configuration:
                      name: name
                      subnet_id: my_AzureFirewallManagementSubnet_subnet
                      public_ip_address_id: my_management_public_ip_addess

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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/azureFirewalls/{firewall_name}"
    response_get = await hub.exec.azure.network.firewall.get(
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
                        "firewall_name": firewall_name,
                        "tags": tags,
                        "location": location,
                        "resource_id": resource_id,
                        "zones": zones,
                        "sku": sku,
                        "firewall_policy_id": firewall_policy_id,
                        "ip_configuration": ip_configuration,
                        "management_ip_configuration": management_ip_configuration,
                    },
                )
                result["comment"].append(
                    f"Would create azure.network.firewall '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = (
                    hub.tool.azure.network.firewall.convert_present_to_raw_firewall(
                        location=location,
                        tags=tags,
                        zones=zones,
                        sku=sku,
                        firewall_policy_id=firewall_policy_id,
                        ip_configuration=ip_configuration,
                        management_ip_configuration=management_ip_configuration,
                    )
                )

                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create firewall {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.firewall.convert_raw_firewall_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    firewall_name=firewall_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(f"Created azure.network.firewall '{name}'")
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.firewall.convert_raw_firewall_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                firewall_name=firewall_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.network.firewall.update_firewall_payload(
                existing_resource, {"tags": tags}
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.firewall '{name}' doesn't need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.firewall.convert_raw_firewall_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        firewall_name=firewall_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.network.firewall '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.firewall '{name}' doesn't need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-06-01",
                success_codes=[200, 201],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.network.firewall {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.firewall.convert_raw_firewall_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                firewall_name=firewall_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Updated azure.network.firewall '{name}'")
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.firewall {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    firewall_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete a firewall.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        firewall_name(str): The name of the firewall.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.firewall.absent:
                - name: my-fp
                - subscription_id: my-subscription
                - resource_group_name: my-resource-group
                - firewall_name: my-fp
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
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/azureFirewalls/{firewall_name}"
    response_get = await hub.exec.azure.network.firewall.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.network.firewall.convert_raw_firewall_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                firewall_name=firewall_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.network.firewall '{firewall_name}'"
                )
                return result
            if (
                response_get["ret"]["properties"]
                and response_get["ret"]["properties"]["provisioningState"] != "Deleting"
            ):
                response_delete = await hub.exec.request.raw.delete(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                    success_codes=[200, 202],
                )

                if not response_delete["result"]:
                    hub.log.debug(
                        f"Could not delete azure.network.firewall {response_delete['comment']} {response_delete['ret']}"
                    )
                    result["result"] = False
                    result["comment"] = [
                        response_delete["comment"],
                        response_delete["ret"],
                    ]
                    return result

            result["comment"].append(
                f"Deleted azure.network.firewall '{firewall_name}'"
            )
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.network.firewall '{firewall_name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not azure.network.firewall '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all firewall under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.firewall
    """
    result = {}
    ret_list = await hub.exec.azure.network.firewall.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe network firewall {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.firewall.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
