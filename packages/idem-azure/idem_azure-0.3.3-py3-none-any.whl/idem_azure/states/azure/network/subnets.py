"""State module for managing Subnets."""
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
    subnet_name: str,
    address_prefix: str,
    enforce_private_link_endpoint_network_policies: bool = None,
    delegations: List[
        make_dataclass(
            "DelegationSet",
            [
                ("name", str, field(default=None)),
                ("service", str, field(default=None)),
            ],
        )
    ] = None,
    enforce_private_link_service_network_policies: bool = None,
    service_endpoints: List = None,
    service_endpoint_policy_ids: List = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or updates Subnets.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        subnet_name(str): The name of the subnet.
        address_prefix(str): The address prefix for the subnet.
        enforce_private_link_endpoint_network_policies(bool, Optional): Enable or Disable apply network policies on private end point in the subnet.
        delegations(list, Optional): An array of references to the delegations on the subnet. Defaults to None

            * name(str, Optional):
                The name of the resource that is unique within a subnet.
            * service(str, Optional):
                The name of the service to whom the subnet should be delegated.
        enforce_private_link_service_network_policies(bool, Optional): Enable or Disable apply network policies on private link service in the subnet.
        service_endpoints(list, Optional): An array of service endpoints
        service_endpoint_policy_ids(list, Optional): An array of service endpoint policy Ids.\
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Subnet resource id on Azure

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-subnet:
              azure.network.subnets.present:
                - name: my-subnet
                - resource_group_name: my-resource-group
                - subscription_id: my-subscription
                - virtual_network_name: my-vnet
                - subnet_name: my-subnet-1
                - address_prefix: 10.0.0.0/24
                - enforce_private_link_endpoint_network_policies: True/False
                - delegations:
                    - name: my-delegation-1
                      service: Microsoft.StoragePool/diskPools
                - enforce_private_link_service_network_policies: True/False
                - service_endpoints:
                    - Microsoft.Sql
                    - Microsoft.Storage
                - service_endpoint_policy_ids:
                    - /subscriptions/subscription_id/resourceGroups/resource_group_name/providers/Microsoft.Network/serviceEndpointPolicies/service_endpoint_policy_name
                    - /subscriptions/subscription_id/resourceGroups/resource_group_name/providers/Microsoft.Network/serviceEndpointPolicies/service_endpoint_policy_name

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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/subnets/{subnet_name}"

    response_get = await hub.exec.azure.network.subnets.get(
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
                        "subscription_id": subscription_id,
                        "virtual_network_name": virtual_network_name,
                        "subnet_name": subnet_name,
                        "address_prefix": address_prefix,
                        "enforce_private_link_endpoint_network_policies": enforce_private_link_endpoint_network_policies,
                        "delegations": delegations,
                        "enforce_private_link_service_network_policies": enforce_private_link_service_network_policies,
                        "service_endpoints": service_endpoints,
                        "service_endpoint_policy_ids": service_endpoint_policy_ids,
                        "resource_id": resource_id,
                    },
                )
                result["comment"].append(f"Would create azure.network.subnets '{name}'")
                return result

            else:
                # PUT operation to create a resource.
                payload = hub.tool.azure.network.subnets.convert_present_to_raw_subnets(
                    address_prefix=address_prefix,
                    enforce_private_link_endpoint_network_policies=enforce_private_link_endpoint_network_policies,
                    delegations=delegations,
                    enforce_private_link_service_network_policies=enforce_private_link_service_network_policies,
                    service_endpoints=service_endpoints,
                    service_endpoint_policy_ids=service_endpoint_policy_ids,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/subnets/{subnet_name}?api-version=2021-03-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.network.subnets '{name}' {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                result[
                    "new_state"
                ] = hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    virtual_network_name=virtual_network_name,
                    subnet_name=subnet_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(f"Created azure.network.subnets '{name}'")
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                subnet_name=subnet_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.network.subnets.update_subnets_payload(
                existing_resource,
                {
                    "address_prefix": address_prefix,
                    "enforce_private_link_endpoint_network_policies": enforce_private_link_endpoint_network_policies,
                    "delegations": delegations,
                    "enforce_private_link_service_network_policies": enforce_private_link_service_network_policies,
                    "service_endpoints": service_endpoints,
                    "service_endpoint_policy_ids": service_endpoint_policy_ids,
                },
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.subnets '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        virtual_network_name=virtual_network_name,
                        subnet_name=subnet_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.network.subnets '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.subnets '{name}' has no property need to be updated."
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
                    f"Could not update azure.network.subnets {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.subnets.convert_raw_subnets_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                virtual_network_name=virtual_network_name,
                subnet_name=subnet_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.network.subnets '{name}' has no property need to be updated."
                )
            result["comment"].append(f"Updated azure.network.subnets '{name}'")
            return result

    else:
        hub.log.debug(
            f"Could not get azure.network.subnets {response_get['comment']} {response_get['ret']}"
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
    subnet_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete Subnets.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_network_name(str): The name of the virtual network.
        subnet_name(str): The name of the subnet.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            my-subnet:
              azure.network.subnets.absent:
                - name: my-subnet
                - resource_group_name: my-resource-group
                - virtual_network_name: my-vnet
                - subnet_name: my-subnet-1
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
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network_name}/subnets/{subnet_name}"

    response_get = await hub.exec.azure.network.subnets.get(
        ctx,
        resource_id=resource_id,
    )

    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name

            if ctx.get("test", False):
                result["comment"].append(f"Would delete azure.network.subnets '{name}'")
                return result

            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200, 202, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.subnets{response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(f"Deleted azure.network.subnets '{name}'")
            return result

        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(f"azure.network.subnets '{name}' already absent")
            return result

    else:
        hub.log.debug(
            f"Could not get azure.network.subnets '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Subnets under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.subnets
    """
    result = {}
    ret_list = await hub.exec.azure.network.subnets.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe subnet {ret_list['comment']}")
        return result
    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.subnets.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
