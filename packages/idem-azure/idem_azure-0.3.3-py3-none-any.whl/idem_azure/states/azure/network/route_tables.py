"""State module for managing Route Tables."""
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
    route_table_name: str,
    location: str,
    routes: List[
        make_dataclass(
            "RouteSet",
            [
                ("route_name", str),
                ("address_prefix", str),
                ("next_hop_type", str),
                ("next_hop_ip_address", str, field(default=None)),
            ],
        )
    ] = None,
    disable_bgp_route_propagation: bool = None,
    tags: Dict = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> dict:
    r"""Create or update Route Tables.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        route_table_name(str): The name of the route table.
        location(str): Resource location. This field can not be updated.
        routes(list, Optional): An array of routes on the route table. Collection of routes contained within a route table.
         Defaults to None.

         * route_name(str):
            The name of the resource that is unique within a resource group.
         * address_prefix(str):
            The destination CIDR to which the route applies.
         * next_hop_type(str):
            The type of Azure hop the packet should be sent to.
         * next_hop_ip_address(str, Optional):
            The IP address packets should be forwarded to. Next hop values are only allowed in routes where the next hop type is VirtualAppliance.
        disable_bgp_route_propagation(bool, Optional): Whether to disable the routes learned by BGP on that route table. True means disable.
        tags(dict[str, str], Optional): Resource tags.
        subscription_id: Subscription Unique id.
        resource_id: Route table resource id on Azure.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.route_tables.present:
              - name: resource_name
              - resource_group_name: my-resource-group
              - route_table_name: my-route-table
              - location: southindia
              - tags:
                  environment: scaleperf
              - disable_bgp_route_propagation: false
              - routes:
                - address_prefix: 10.0.0.0/26
                  next_hop_ip_address: 10.0.1.0
                  next_hop_type: VirtualAppliance
                  route_name: my-route
                - address_prefix: 10.0.0.0/25
                  next_hop_type: None
                  route_name: my-route-2
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/routeTables/{route_table_name}"
    response_get = await hub.exec.azure.network.route_tables.get(
        ctx, resource_id=resource_id, raw=True
    )

    if response_get["result"]:
        if response_get["ret"] is None:
            if ctx.get("test", False):
                result[
                    "new_state"
                ] = hub.tool.azure.test_state_utils.generate_test_state(
                    enforced_state={},
                    desired_state={
                        "name": name,
                        "resource_group_name": resource_group_name,
                        "route_table_name": route_table_name,
                        "location": location,
                        "routes": routes,
                        "resource_id": resource_id,
                        "disable_bgp_route_propagation": disable_bgp_route_propagation,
                        "tags": tags,
                        "subscription_id": subscription_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.network.route_tables '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.network.route_tables.convert_present_to_raw_route_tables(
                    location=location,
                    routes=routes,
                    disable_bgp_route_propagation=disable_bgp_route_propagation,
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
                        f"Could not create azure.network.route_tables {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result
                result[
                    "new_state"
                ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    route_table_name=route_table_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(f"Created azure.network.route_tables '{name}'")
                return result
        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_table_name=route_table_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = (
                hub.tool.azure.network.route_tables.update_route_table_payload(
                    existing_resource,
                    {
                        "location": location,
                        "routes": routes,
                        "disable_bgp_route_propagation": disable_bgp_route_propagation,
                        "tags": tags,
                    },
                )
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.route_tables '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        route_table_name=route_table_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )

                    result["comment"].append(
                        f"Would update azure.network.route_tables '{name}'"
                    )
                return result
            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.route_tables '{name}' has no property need to be updated."
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
                    f"Could not update azure.network.route_tables {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_table_name=route_table_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Updated azure.network.route_tables '{name}'")
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.route_tables {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    route_table_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete Route Tables.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        route_table_name(str): The name of the route table.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.route_tables.absent:
                - name: my-resource
                - resource_group_name: my-resource-group-name
                - route_table_name: my-route-table
    """
    result = dict(name=name, result=True, comment=[], old_state=None, new_state=None)
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/routeTables/{route_table_name}"
    response_get = await hub.exec.azure.network.route_tables.get(
        ctx, resource_id=resource_id, raw=True
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.network.route_tables.convert_raw_route_tables_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_table_name=route_table_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.network.route_tables '{name}'"
                )
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-03-01",
                success_codes=[200, 202, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.route_tables {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(f"Deleted azure.network.route_tables '{name}'")
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.network.route_tables '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.route_tables {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Route Tables under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.route_tables
    """
    result = {}
    ret_list = await hub.exec.azure.network.route_tables.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe network route_tables {ret_list['comment']}")
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.network.route_tables.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }

    return result
