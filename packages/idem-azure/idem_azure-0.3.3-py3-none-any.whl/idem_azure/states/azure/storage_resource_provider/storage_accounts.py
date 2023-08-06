"""State module for managing Storage Accounts."""
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
    account_name: str,
    location: str,
    sku_tier: str,
    sku_name: str,
    account_kind: str = None,
    cross_tenant_replication_enabled: bool = None,
    access_tier: str = None,
    edge_zone: str = None,
    enable_https_traffic_only: bool = None,
    min_tls_version: str = None,
    allow_blob_public_access: bool = None,
    allow_shared_key_access: bool = None,
    public_network_access: str = None,
    default_to_oauth_authentication: bool = None,
    is_hns_enabled: bool = None,
    nfsv3_enabled: bool = None,
    custom_domain: make_dataclass(
        "CustomDomain",
        [
            ("name", str),
            ("use_subdomain", bool, field(default=None)),
        ],
    ) = None,
    customer_managed_key: make_dataclass(
        "CustomerManagedKey",
        [("key_vault_key_id", str), ("user_assigned_identity_id", str)],
    ) = None,
    identity: make_dataclass(
        "Identity",
        [
            ("type", str),
            ("user_assigned_identities", Dict[str, str], field(default=None)),
        ],
    ) = None,
    network_rules: make_dataclass(
        "NetworkRules",
        [
            ("default_action", str),
            ("bypass", str, field(default=None)),
            ("ip_rule_values", List[str], field(default=None)),
            ("virtual_network_subnet_ids", List[str], field(default=None)),
            (
                "resource_access_rules",
                List[
                    make_dataclass(
                        "ResourceAccessRules",
                        [
                            ("endpoint_resource_id", str),
                            ("endpoint_tenant_id", str, field(default=None)),
                        ],
                    )
                ],
                field(default=None),
            ),
        ],
    ) = None,
    large_file_shares_state: str = None,
    azure_files_authentication: make_dataclass(
        "AzureFilesAuthentication",
        [
            ("directory_service_options", str),
            (
                "active_directory_properties",
                make_dataclass(
                    "ActiveDirectoryProperties",
                    [
                        ("azure_storage_sid", str),
                        ("domain_name", str),
                        ("domain_sid", str),
                        ("domain_guid", str),
                        ("forest_name", str),
                        ("netbios_domain_name", str),
                    ],
                ),
                field(default=None),
            ),
        ],
    ) = None,
    routing: make_dataclass(
        "Routing",
        [
            ("publish_internet_endpoints", bool, field(default=None)),
            ("publish_microsoft_endpoints", bool, field(default=None)),
            ("routing_choice", str, field(default=None)),
        ],
    ) = None,
    encryption_service: make_dataclass(
        "EncryptionService",
        [
            ("encryption_key_source", str, field(default="Microsoft.Storage")),
            ("queue_encryption_key_type", str, field(default=None)),
            ("table_encryption_key_type", str, field(default=None)),
        ],
    ) = None,
    require_infrastructure_encryption: bool = None,
    immutability_policy: make_dataclass(
        "ImmutabilityPolicy",
        [
            ("allow_protected_append_writes", bool),
            ("state", str),
            ("period_since_creation_in_days", int),
        ],
    ) = None,
    sas_policy: make_dataclass(
        "SasPolicy",
        [
            ("expiration_period", str),
            ("expiration_action", str, field(default="Log")),
        ],
    ) = None,
    allowed_copy_scope: str = None,
    sftp_enabled: bool = None,
    tags: Dict[str, str] = None,
    subscription_id: str = None,
    resource_id: str = None,
) -> Dict:
    r"""Create or update Storage Accounts.

    Args:
        name(str): The identifier for this state.
        account_name(str): The name of the storage account within the specified resource group. Storage account names
            must be between 3 and 24 characters in length and use numbers and lower-case letters only.
        resource_group_name(str): The name of the resource group.
        location(str): Specifies the supported Azure location where the resource exists.
        sku_tier(str): The SKU tier
        sku_name(str): The SKU name
        account_kind(str, Optional): Defines the Kind of account.
        cross_tenant_replication_enabled(bool, Optional): Allow or disallow cross AAD tenant object replication
        access_tier(str, Optional): Required for storage accounts where account_kind = BlobStorage. The access tier is used for billing
        edge_zone(str, Optional): Specifies the Edge Zone within the Azure Region where this Storage Account should exist.
        enable_https_traffic_only(bool, Optional): Boolean flag which forces HTTPS if enabled.
        min_tls_version(str, Optional): The minimum supported TLS version for the storage account.
        allow_blob_public_access(bool, Optional): Allow or disallow nested items within this Account to opt into being public.
        allow_shared_key_access(bool, Optional): Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key.
        public_network_access(str, Optional): Allow or disallow public network access to Storage Account. Value is optional but if passed in, must be 'Enabled' or 'Disabled'.
        default_to_oauth_authentication(bool, Optional): A boolean flag which indicates whether the default authentication is OAuth or not. The default interpretation is false for this property.
        is_hns_enabled(bool, Optional): Account HierarchicalNamespace enabled if sets to true.
        nfsv3_enabled(bool, Optional): NFS 3.0 protocol support enabled if set to true.
        custom_domain(dict[str, Any], Optional): User domain assigned to the storage account.

            * name(str):
                The Custom Domain Name to use for the Storage Account
            * use_subdomain(bool, Optional):
                Indicates whether indirect CName validation is enabled. Default value is false
        customer_managed_key(dict[str, Any], Optional): Combination of Key vault key id and user assigned id

            * user_assigned_identity_id(str):
                User Assigned Identity id
            * key_vault_key_id(str):
                The object identifier of the current versioned Key Vault Key in use.
        identity(dict[str, Any], Optional): The identity of the resource.

            * type(str):
                The identity type. Possible values are SystemAssigned, UserAssigned, SystemAssigned, UserAssigned
            * user_assigned_identities(dict[str, Any], Optional):
                Key value pairs that describe the set of User Assigned identities that will be used with this storage account
        network_rules(dict[str, Any], Optional): Network rule set

            * default_action(str):
                Specifies the default action of allow or deny when no other rules match. Valid options are Deny or Allow
            * bypass(str, Optional):
                Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging|Metrics|AzureServices
            * ip_rule_values(list, Optional):
                List of IP or IP range in CIDR format. Only IPV4 address is allowed.
            * virtual_network_subnet_ids(list, Optional):
                A list of resource ids of virtual network subnets.
            * resource_access_rules(dict[str, Any], Optional):
                The resource access rules
        large_file_shares_state(str, Optional): Allow large file shares if sets to enable.
        azure_files_authentication(dict[str, Any], Optional): Provides the identity based authentication settings for Azure Files.

            * directory_service_options(str):
                The directory service to be used. Possible values are AADDS, AD and AADKERB.
            * active_directory_properties(dict[str, Any], Optional):
                Required if directoryServiceOptions are AD, optional if they are AADKERB.
        routing(dict[str, Any], Optional): Maintains information about the network routing choice opted by the user for data transfer.

            * publish_internet_endpoints(bool, Optional):
                A boolean flag which indicates whether internet routing storage endpoints are to be published.
            * publish_microsoft_endpoints(bool, Optional):
                A boolean flag which indicates whether microsoft routing storage endpoints are to be published.
            * routing_choice(str, Optional):
                Routing Choice defines the kind of network routing opted by the user.
        encryption_service(dict[str, Any], Optional): Encryption details

            * queue_encryption_key_type(str, Optional):
                The encryption type of the queue service.
            * table_encryption_key_type(str, Optional):
                The encryption type of the table service.
            * encryption_key_source(str, Optional):
                The encryption keySource (provider)
        require_infrastructure_encryption(bool, Optional): A boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest.
        immutability_policy(dict[str, Any], Optional): This argument specifies the default account-level immutability policy which is inherited and applied to objects.

            * allow_protected_append_writes(bool):
                This property can only be changed for disabled and unlocked time-based retention policies. When enabled, new blocks can be written to an append blob while
                maintaining immutability protection and compliance. Only new blocks can be added and any existing blocks cannot be modified or deleted.
            * state(str):
                Defines the mode of the policy. Disabled state disables the policy, Unlocked state
                allows increase and decrease of immutability retention time and also allows toggling allowProtectedAppendWrites property,
                Locked state only allows the increase of the immutability retention time. A policy can only be created
                in a Disabled or Unlocked state and can be toggled between the two states. Only a policy in an Unlocked
                state can transition to a Locked state which cannot be reverted.
            * period_since_creation_in_days(int): The immutability period for the blobs in the container since the policy creation, in days.
        sas_policy(dict[str, Any], Optional): SasPolicy assigned to the storage account.

            * expiration_period(str, Optional):
                The SAS expiration period, DD.HH:MM:SS.
            * expiration_action(str, Optional):
                The SAS expiration action. Valid value is Log.

        allowed_copy_scope(str, Optional): Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet.
        sftp_enabled(bool, Optional): Enables Secure File Transfer Protocol, if set to true
        tags(dict[str, str], Optional): The resource tags.
        subscription_id(str, Optional): Subscription Unique id.
        resource_id(str, Optional): Storage account resource id on Azure.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.storage_resource_provider.storage_accounts.present:
                - name: value
                - resource_group_name: value
                - account_name: value
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
        resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{account_name}"

    response_get = await hub.exec.azure.storage_resource_provider.storage_accounts.get(
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
                        "account_name": account_name,
                        "location": location,
                        "sku_tier": sku_tier,
                        "sku_name": sku_name,
                        "account_kind": account_kind,
                        "cross_tenant_replication_enabled": cross_tenant_replication_enabled,
                        "access_tier": access_tier,
                        "edge_zone": edge_zone,
                        "enable_https_traffic_only": enable_https_traffic_only,
                        "min_tls_version": min_tls_version,
                        "allow_blob_public_access": allow_blob_public_access,
                        "allow_shared_key_access": allow_shared_key_access,
                        "public_network_access": public_network_access,
                        "default_to_oauth_authentication": default_to_oauth_authentication,
                        "is_hns_enabled": is_hns_enabled,
                        "nfsv3_enabled": nfsv3_enabled,
                        "custom_domain": custom_domain,
                        "customer_managed_key": customer_managed_key,
                        "identity": identity,
                        "network_rules": network_rules,
                        "large_file_shares_state": large_file_shares_state,
                        "azure_files_authentication": azure_files_authentication,
                        "routing": routing,
                        "encryption_service": encryption_service,
                        "require_infrastructure_encryption": require_infrastructure_encryption,
                        "immutability_policy": immutability_policy,
                        "sas_policy": sas_policy,
                        "allowed_copy_scope": allowed_copy_scope,
                        "sftp_enabled": sftp_enabled,
                        "tags": tags,
                        "resource_id": resource_id,
                        "subscription_id": subscription_id,
                    },
                )
                result["comment"].append(
                    f"Would create azure.storage_resource_provider.storage_accounts '{name}'"
                )
                return result
            else:
                # PUT operation to create a resource
                payload = hub.tool.azure.storage_resource_provider.storage_accounts.convert_present_to_raw_storage_accounts(
                    location=location,
                    sku_tier=sku_tier,
                    sku_name=sku_name,
                    account_kind=account_kind,
                    cross_tenant_replication_enabled=cross_tenant_replication_enabled,
                    access_tier=access_tier,
                    edge_zone=edge_zone,
                    enable_https_traffic_only=enable_https_traffic_only,
                    min_tls_version=min_tls_version,
                    allow_blob_public_access=allow_blob_public_access,
                    allow_shared_key_access=allow_shared_key_access,
                    public_network_access=public_network_access,
                    default_to_oauth_authentication=default_to_oauth_authentication,
                    is_hns_enabled=is_hns_enabled,
                    nfsv3_enabled=nfsv3_enabled,
                    custom_domain=custom_domain,
                    customer_managed_key=customer_managed_key,
                    identity=identity,
                    network_rules=network_rules,
                    large_file_shares_state=large_file_shares_state,
                    azure_files_authentication=azure_files_authentication,
                    routing=routing,
                    encryption_service=encryption_service,
                    require_infrastructure_encryption=require_infrastructure_encryption,
                    immutability_policy=immutability_policy,
                    sas_policy=sas_policy,
                    allowed_copy_scope=allowed_copy_scope,
                    sftp_enabled=sftp_enabled,
                    tags=tags,
                )
                response_put = await hub.exec.request.json.put(
                    ctx,
                    url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                    success_codes=[200, 201],
                    json=payload,
                )

                if response_put["status"] == 202:
                    get_response = {"result": False}
                    while not get_response["result"]:
                        get_response = await hub.exec.request.json.get(
                            ctx,
                            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                            success_codes=[200],
                        )
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                        resource=get_response["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        account_name=account_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )

                elif not response_put["result"] and response_put["status"] != 202:
                    hub.log.debug(
                        f"Could not create azure.storage_resource_provider.storage_accounts {response_put['comment']} {response_put['ret']}"
                    )
                    result["comment"] = [response_put["comment"], response_put["ret"]]
                    result["result"] = False
                    return result

                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                        resource=response_put["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        account_name=account_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )

                result["comment"].append(
                    f"Created azure.storage_resource_provider.storage_accounts '{name}'"
                )
                return result

        else:
            existing_resource = response_get["ret"]
            result[
                "old_state"
            ] = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                resource=existing_resource,
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                account_name=account_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            # Generate a new PUT operation payload with new values
            new_payload = hub.tool.azure.storage_resource_provider.storage_accounts.update_storage_accounts_payload(
                existing_resource,
                {
                    "sku_tier": sku_tier,
                    "sku_name": sku_name,
                    "account_kind": account_kind,
                    "cross_tenant_replication_enabled": cross_tenant_replication_enabled,
                    "access_tier": access_tier,
                    "edge_zone": edge_zone,
                    "enable_https_traffic_only": enable_https_traffic_only,
                    "min_tls_version": min_tls_version,
                    "allow_blob_public_access": allow_blob_public_access,
                    "allow_shared_key_access": allow_shared_key_access,
                    "public_network_access": public_network_access,
                    "default_to_oauth_authentication": default_to_oauth_authentication,
                    "is_hns_enabled": is_hns_enabled,
                    "nfsv3_enabled": nfsv3_enabled,
                    "custom_domain": custom_domain,
                    "customer_managed_key": customer_managed_key,
                    "identity": identity,
                    "network_rules": network_rules,
                    "large_file_shares_state": large_file_shares_state,
                    "azure_files_authentication": azure_files_authentication,
                    "routing": routing,
                    "encryption_service": encryption_service,
                    # "queue_encryption_key_type": queue_encryption_key_type,
                    # "table_encryption_key_type": table_encryption_key_type,
                    # "encryption_key_source": encryption_key_source,
                    "require_infrastructure_encryption": require_infrastructure_encryption,
                    "immutability_policy": immutability_policy,
                    "sas_policy": sas_policy,
                    "allowed_copy_scope": allowed_copy_scope,
                    "sftp_enabled": sftp_enabled,
                    "tags": tags,
                },
            )

            if ctx.get("test", False):
                if new_payload["ret"] is None:
                    result["new_state"] = copy.deepcopy(result["old_state"])
                    result["comment"].append(
                        f"azure.storage_resource_provider.storage_accounts '{name}' has no property need to be updated."
                    )
                else:
                    result[
                        "new_state"
                    ] = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                        resource=new_payload["ret"],
                        idem_resource_name=name,
                        resource_group_name=resource_group_name,
                        account_name=account_name,
                        resource_id=resource_id,
                        subscription_id=subscription_id,
                    )
                    result["comment"].append(
                        f"Would update azure.storage_resource_provider.storage_accounts '{name}'"
                    )
                return result

            # PUT operation to update a resource
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.storage_resource_provider.storage_accounts '{name}' has no property need to be updated."
                )
                return result
            result["comment"] = result["comment"] + new_payload["comment"]

            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                success_codes=[200],
                json=new_payload["ret"],
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not update azure.storage_resource_provider.storage_accounts {response_put['comment']} {response_put['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_put["comment"], response_put["ret"]]
                return result

            result[
                "new_state"
            ] = hub.tool.azure.storage_resource_provider.storage_accounts.convert_raw_storage_accounts_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                resource_group_name=resource_group_name,
                account_name=account_name,
                resource_id=resource_id,
                subscription_id=subscription_id,
            )
            if result["old_state"] == result["new_state"]:
                result["comment"].append(
                    f"azure.storage_resource_provider.storage_accounts '{name}' has no property need to be updated."
                )
                return result
            result["comment"].append(
                f"Updated azure.storage_resource_provider.storage_accounts '{name}'"
            )
            return result

    else:
        hub.log.debug(
            f"Could not get azure.storage_resource_provider.storage_accounts {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    account_name: str,
    subscription_id: str = None,
) -> dict:
    r"""Delete Storage Accounts.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        account_name(str): The name of the storage account within the specified resource group.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.storage_resource_provider.storage_accounts.absent:
                - name: value
                - resource_group_name: value
                - account_name: value
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
    resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Storage/storageAccounts/{account_name}"

    response_get = await hub.exec.azure.storage_resource_provider.storage_accounts.get(
        ctx,
        resource_id=resource_id,
    )

    if response_get["result"]:
        if response_get["ret"]:
            result["old_state"] = response_get["ret"]
            result["old_state"]["name"] = name

            if ctx.get("test", False):
                result["comment"].append(
                    f"Would delete azure.storage_resource_provider.storage_accounts '{name}'"
                )
                return result

            response_delete = await hub.exec.request.raw.delete(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2021-04-01",
                success_codes=[200, 204],
            )

            if not response_delete["result"]:
                hub.log.debug(
                    f"Could not delete azure.storage_resource_provider.storage_accounts '{name}' {response_delete['comment']} {response_delete['ret']}"
                )
                result["result"] = False
                result["comment"] = [response_delete["comment"], response_delete["ret"]]
                return result

            result["comment"].append(
                f"Deleted azure.storage_resource_provider.storage_accounts '{name}'"
            )
            return result

        else:
            # If Azure returns 'Not Found' error, it means the resource has been absent.
            result["comment"].append(
                f"azure.storage_resource_provider.storage_accounts '{name}' already absent"
            )
            return result
    else:
        hub.log.debug(
            f"Could not get azure.storage_resource_provider.storage_accounts '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
    return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Storage Accounts under the same subscription.

    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.storage_resource_provider.storage_accounts
    """
    result = {}
    ret_list = await hub.exec.azure.storage_resource_provider.storage_accounts.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(f"Could not describe storage account {ret_list['comment']}")
        return result
    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.storage_resource_provider.storage_accounts.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
