"""State module for managing Route."""
import copy
from typing import Any
from typing import Dict


async def present(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    route_table_name: str,
    route_name: str,
    address_prefix: str,
    next_hop_type: str,
    next_hop_ip_address: str = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> dict:
    r"""Create or update Routes.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        route_table_name(str): The name of the route table.
        route_name(str): The name of the route.
        address_prefix(str): Resource location. This field can not be updated.
        next_hop_type(str): The type of Azure hop the packet should be sent to.
        next_hop_ip_address(str, Optional): The IP address packets should be forwarded to. Next hop values are only allowed in routes where the next hop type is VirtualAppliance.
        subscription_id: Subscription Unique id.
        resource_id: Route table resource id on Azure.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.routes.present:
              - name: resource_name
              - resource_group_name: my-resource-group
              - route_name: my-route
              - route_table_name: my-route-table
              - address_prefix:10.0.0.0/25
              - next_hop_ip_address: 10.0.1.0
              - next_hop_type: VirtualAppliance
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/routeTables/{route_table_name}/routes/{route_name}"
    response_get = await hub.exec.azure.network.routes.get(
        ctx,
        resource_id=resource_id,
        raw=True,
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
                        "route_name": route_name,
                        "address_prefix": address_prefix,
                        "next_hop_type": next_hop_type,
                        "next_hop_ip_address": next_hop_ip_address,
                        "resource_id": resource_id,
                        "subscription_id": subscription_id,
                    },
                )
                result["comment"].append(f"Would create azure.network.routes '{name}'")
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.network.routes.convert_present_to_raw_routes(
                    address_prefix=address_prefix,
                    next_hop_type=next_hop_type,
                    next_hop_ip_address=next_hop_ip_address,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                    success_codes=[200, 201],
                    json=payload,
                )
                if not response_put["result"]:
                    hub.log.debug(
                        f"Could not create azure.network.routes {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result
                result[
                    "new_state"
                ] = hub.tool.azure.network.routes.convert_raw_routes_to_present(
                    resource=response_put["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    route_table_name=route_table_name,
                    route_name=route_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(f"Created azure.network.routes '{name}'")
                return result
        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.network.routes.convert_raw_routes_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_name=route_name,
                route_table_name=route_table_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.network.routes.update_route_payload(
                existing_resource,
                {
                    "address_prefix": address_prefix,
                    "next_hop_type": next_hop_type,
                    "next_hop_ip_address": next_hop_ip_address,
                },
            )
            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.network.routes '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.network.routes.convert_raw_routes_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        route_table_name=route_table_name,
                        route_name=route_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )

                    result["comment"].append(
                        f"Would update azure.network.routes '{name}'"
                    )
                return result
            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.routes '{name}' has no property need to be updated."
                )
                return result
            result["comment"] += new_payload["comment"]
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                success_codes=[200],
                json=new_payload["ret"],
            )

            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.network.routes {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.routes.convert_raw_routes_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_table_name=route_table_name,
                route_name=route_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(f"Updated azure.network.routes '{name}'")
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.routes {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


__contracts__ = ["resource"]


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    route_table_name: str,
    route_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete Routes.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        route_name(str): The name of the route.
        route_table_name(str): The name of the route table.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.routes.absent:
                - name: my-resource
                - resource_group_name: my-resource-group-name
                - route_name: my-route
                - route_table_name: my-route-table
    """
    result = dict(name=name, result=True, comment=[], old_state=None, new_state=None)
    if subscription_id is None:
        subscription_id = ctx.acct.subscription_id
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/routeTables/{route_table_name}/routes/{route_name}"
    response_get = await hub.exec.azure.network.routes.get(
        ctx,
        resource_id=resource_id,
        raw=True,
    )
    if response_get["result"]:
        if response_get["ret"]:
            result[
                "old_state"
            ] = hub.tool.azure.network.routes.convert_raw_routes_to_present(
                resource=response_get["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                route_name=route_name,
                route_table_name=route_table_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if ctx.get("test", False):
                result["comment"].append(f"Would delete azure.network.routes '{name}'")
                return result
            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                success_codes=[200, 202, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.network.routes {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(f"Deleted azure.network.routes '{name}'")
            return result
        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(f"azure.network.routes '{name}' already absent")
            return result
    else:
        hub.log.debug(
            f"Could not get azure.network.routes {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Route under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.routes
    """
    result = {}
    ret = await hub.exec.azure.network.routes.list(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe network routes {ret['comment']}")
        return {}

    for route in ret["ret"]:
        resource_id = route.get("resource_id")
        result[resource_id] = {
            "azure.network.routes.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in route.items()
            ]
        }
    return result
