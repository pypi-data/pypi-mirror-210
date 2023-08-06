"""States module for managing Firewall Policy."""
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
    firewall_policy_name: str,
    subscription_id: str = None,
    tags: Dict = None,
    base_policy_id: str = None,
    threat_intelligence_allow_list: make_dataclass(
        "threatIntelligenceAllowList",
        [
            ("fqdns", List[str], field(default=None)),
            ("ip_addresses", List[str], field(default=None)),
        ],
    ) = None,
    dns_settings: make_dataclass(
        "dnsSettings",
        [
            ("proxy_enabled", bool, field(default=None)),
            ("servers", List[str], field(default=None)),
        ],
    ) = None,
    sku: make_dataclass(
        "sku",
        [("tier", str, field(default=None))],
    ) = None,
    intrusion_detection: make_dataclass(
        "intrusionDetection",
        [("mode", str)],
    ) = None,
    threat_intelligence_mode: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Firewall Policy.

    Args:
        name(str): The identifier for this state.
        location(str): Resource location. Changing this forces a new resource to be created.
        resource_group_name(str): The name of the resource group.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Firewall Policy resource id on Azure
        tags(dict[str, str], Optional): Resource tags.
        firewall_policy_name(str): The name of the firewall policy.
        base_policy_id(str, Optional): The ID of the base Firewall Policy.
        threat_intelligence_allow_list(dict[str, Any], Optional): Specifies threat_intelligence_allowlist while creating the Firewall policy.

            * fqdns(list[str]):
                A list of FQDNs that will be skipped for threat detection.
            * ip_addresses(list[str]):
                A list of IP addresses or CIDR ranges that will be skipped for threat detection.
        dns_settings(dict[str, Any], Optional): Specifies dns setting while creating the Firewall policy.

            * proxy_enabled(bool):
                Whether to enable DNS proxy on Firewalls attached to this Firewall Policy.
            * servers(list[str]):
                A list of custom DNS servers' IP addresses.
        sku(dict[str, Any], Optional): The SKU Tier of the Firewall Policy.

            * tier(str):
                Possible values are Standard, Premium and Basic. Changing this forces a new Firewall Policy to be created.
        intrusion_detection(dict[str, Any], Optional): A intrusion_detection block for Firewall policy.

            * mode(str):
                In which mode you want to run intrusion detection: Off, Alert or Deny.
        threat_intelligence_mode(str, Optional): The operation mode for Threat Intelligence. Possible values are Alert, Deny and Off. Defaults to Alert.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.network.firewall_policies.present:
                - name: my_fp
                - subscription_id: my_sub_id
                - resource_group_name: my_rg-1
                - firewall_policy_name: my-fp
                - location: eastus
                - tags:
                    key: value
                - sku:
                    tier: Premium
                - base_policy_id: my_base_pol_id
                - threat_intelligence_allow_list:
                    ip_addresses:
                      - my_ip_address
                    fqdns:
                      - "*"
                - intrusion_detection:
                    mode: Alert
                - threat_intelligence_mode: Alert
                - dns_settings:
                    proxy_enabled: true
                    servers:
                      - my_server
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/firewallPolicies/{firewall_policy_name}"

    response_get = await hub.exec.azure.network.firewall_policies.get(
        ctx, resource_id=resource_id, raw=True
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.network.firewall_policies {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if not response_get["ret"]:
        if ctx.get("test", False):
            # Return a proposed state by Idem state --test
            result["new_state"] = hub.tool.azure.test_state_utils.generate_test_state(
                enforced_state={},
                desired_state={
                    "name": name,
                    "resource_group_name": resource_group_name,
                    "subscription_id": subscription_id,
                    "firewall_policy_name": firewall_policy_name,
                    "tags": tags,
                    "location": location,
                    "resource_id": resource_id,
                    "dns_settings": dns_settings,
                    "sku": sku,
                    "intrusion_detection": intrusion_detection,
                    "threat_intelligence_mode": threat_intelligence_mode,
                    "threat_intelligence_allow_list": threat_intelligence_allow_list,
                    "base_policy_id": base_policy_id,
                },
            )
            result["comment"].append(
                f"Would create azure.network.firewall_policies '{name}'"
            )
            return result
        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.network.firewall_policies.convert_present_to_raw_fire_policies(
                location=location,
                tags=tags,
                dns_settings=dns_settings,
                sku=sku,
                intrusion_detection=intrusion_detection,
                threat_intelligence_mode=threat_intelligence_mode,
                threat_intelligence_allow_list=threat_intelligence_allow_list,
                base_policy_id=base_policy_id,
            )
            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
                success_codes=[200, 201],
                json=payload,
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create firewall policy {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                firewall_policy_name=firewall_policy_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            result["comment"].append(
                f"Created azure.network.firewall_policies '{name}'"
            )
            return result

    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            resource_group_name=resource_group_name,
            firewall_policy_name=firewall_policy_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        # Generate a new PUT operation payload with new values
        new_payload = (
            hub.tool.azure.network.firewall_policies.update_fire_policies_payload(
                existing_resource, {"tags": tags}
            )
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.network.firewall_policies '{name}' doesn't need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    resource_group_name=resource_group_name,
                    firewall_policy_name=firewall_policy_name,
                    resource_id=resource_id,
                    subscription_id=subscription_id,
                )
                result["comment"].append(
                    f"Would update azure.network.firewall_policies '{name}'"
                )
            return result

        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.network.firewall_policies '{name}' doesn't need to be updated."
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
                f"Could not update azure.network.firewall_policies {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_put["comment"], response_put["ret"]]
            return result

        result[
            "new_state"
        ] = hub.tool.azure.network.firewall_policies.convert_raw_firewall_policies_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            resource_group_name=resource_group_name,
            firewall_policy_name=firewall_policy_name,
            resource_id=resource_id,
            subscription_id=subscription_id,
        )
        result["comment"].append(f"Updated azure.network.firewall_policies '{name}'")
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    firewall_policy_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete a firewall policy.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        firewall_policy_name(str): The name of the firewall policy.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.network.firewall_policies.absent:
                - name: my-fp
                - subscription_id: my-subscription
                - resource_group_name: my-resource-group
                - firewall_policy_name: my-fp
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
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/firewallPolicies/{firewall_policy_name}"
    response_get = await hub.exec.azure.network.firewall_policies.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.network.firewall_policies '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name
        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.network.firewall_policies '{firewall_policy_name}'"
            )
            return result
        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-07-01",
            success_codes=[200, 202],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.network.firewall_policies {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(
            f"Deleted azure.network.firewall_policies '{firewall_policy_name}'"
        )
        return result
    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.network.firewall_policies '{firewall_policy_name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all firewall policy under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.network.firewall_policies
    """
    result = {}
    ret = await hub.exec.azure.network.firewall_policies.list(ctx)
    if not ret["result"]:
        hub.log.debug(f"Could not describe network firewall_policies {ret['comment']}")
        return {}

    for resource in ret["ret"]:
        resource_id = resource.get("resource_id")
        result[resource_id] = {
            f"azure.network.firewall_policies.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
