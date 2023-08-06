import copy
from typing import Any
from typing import Dict
from typing import List


def convert_raw_storage_accounts_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    account_name: str,
    resource_id: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Converts raw storage account api response into present function format

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        account_name: Azure storage account group name.
        resource_id: Azure Policy Definition resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    translated_resounrce = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "subscription_id": subscription_id,
        "account_name": account_name,
        "location": resource["location"],
    }

    if resource.get("sku") and resource.get("sku").get("name"):
        translated_resounrce["sku_name"] = resource["sku"]["name"]

    if resource.get("sku") and resource.get("sku").get("tier"):
        translated_resounrce["sku_tier"] = resource["sku"]["tier"]

    if "kind" in resource:
        translated_resounrce["account_kind"] = resource["kind"]

    if resource.get("extendedLocation") and resource.get("extendedLocation").get(
        "name"
    ):
        translated_resounrce["edge_zone"] = resource["extendedLocation"].get("name")

    if "identity" in resource:
        identity_payload = convert_raw_to_present_identity(
            hub, identity=resource["identity"]
        )
        translated_resounrce["identity"] = identity_payload

    if "tags" in resource:
        translated_resounrce["tags"] = resource["tags"]

    properties = resource.get("properties")
    if properties:
        if "allowCrossTenantReplication" in properties:
            translated_resounrce["cross_tenant_replication_enabled"] = properties[
                "allowCrossTenantReplication"
            ]

        if "accessTier" in properties:
            translated_resounrce["access_tier"] = properties["accessTier"]

        if "supportsHttpsTrafficOnly" in properties:
            translated_resounrce["enable_https_traffic_only"] = properties[
                "supportsHttpsTrafficOnly"
            ]

        if "minimumTlsVersion" in properties:
            translated_resounrce["min_tls_version"] = properties["minimumTlsVersion"]

        if "allowBlobPublicAccess" in properties:
            translated_resounrce["allow_blob_public_access"] = properties[
                "allowBlobPublicAccess"
            ]

        if "allowSharedKeyAccess" in properties:
            translated_resounrce["allow_shared_key_access"] = properties[
                "allowSharedKeyAccess"
            ]

        if "publicNetworkAccess" in properties:
            translated_resounrce["public_network_access"] = properties[
                "publicNetworkAccess"
            ]

        if "defaultToOAuthAuthentication" in properties:
            translated_resounrce["default_to_oauth_authentication"] = properties[
                "defaultToOAuthAuthentication"
            ]

        if "isHnsEnabled" in properties:
            translated_resounrce["is_hns_enabled"] = properties["isHnsEnabled"]

        if "isNfsV3Enabled" in properties:
            translated_resounrce["nfsv3_enabled"] = properties["isNfsV3Enabled"]

        if properties.get("customDomain") is not None:
            customDomainPayload = convert_raw_to_present_custom_domain(
                hub, c_domain=properties.get("customDomain")
            )
            translated_resounrce["custom_domain"] = customDomainPayload

        if properties.get("encryption") is not None:
            customerManagedKeyPayload = convert_raw_to_present_customer_managed_key(
                hub, customer_key=properties.get("encryption")
            )
            if len(customerManagedKeyPayload) != 0:
                translated_resounrce["customer_managed_key"] = customerManagedKeyPayload

        if properties.get("networkAcls") is not None:
            networkRulesPayload = convert_raw_to_present_network_rules(
                hub, rules=properties.get("networkAcls")
            )
            translated_resounrce["network_rules"] = networkRulesPayload

        if "largeFileSharesState" in properties:
            translated_resounrce["large_file_shares_state"] = properties[
                "largeFileSharesState"
            ]

        if properties.get("azureFilesIdentityBasedAuthentication") is not None:
            authPayload = convert_raw_to_present_files_authentication(
                hub, file_auth=properties.get("azureFilesIdentityBasedAuthentication")
            )
            translated_resounrce["azure_files_authentication"] = authPayload

        if properties.get("routingPreference") is not None:
            routing_payload = convert_raw_to_present_routing(
                hub, routing_pref=properties.get("routingPreference")
            )
            translated_resounrce["routing"] = routing_payload

        if properties.get("encryption") is not None:
            encryptionServicePayload = convert_raw_to_present_encryption_service(
                hub, encryption_service=properties.get("encryption")
            )
            translated_resounrce["encryption_service"] = encryptionServicePayload

        if (properties.get("encryption") is not None) and (
            properties.get("encryption").get("requireInfrastructureEncryption")
            is not None
        ):
            translated_resounrce["require_infrastructure_encryption"] = properties[
                "encryption"
            ]["requireInfrastructureEncryption"]

        if (properties.get("immutableStorageWithVersioning") is not None) and (
            properties.get("immutableStorageWithVersioning").get("immutabilityPolicy")
            is not None
        ):
            immutableStoragePayload = convert_raw_to_present_immutability_policy(
                hub,
                immutePolicy=properties.get("immutableStorageWithVersioning").get(
                    "immutabilityPolicy"
                ),
            )
            translated_resounrce["immutability_policy"] = immutableStoragePayload

        if properties.get("sasPolicy") is not None:
            sasPolicyPayload = convert_raw_to_present_sas_policy(
                hub, policy=properties.get("sasPolicy")
            )
            translated_resounrce["sas_policy"] = sasPolicyPayload

        if "allowedCopyScope" in properties:
            translated_resounrce["allowed_copy_scope"] = properties["allowedCopyScope"]

        if "isSftpEnabled" in properties:
            translated_resounrce["sftp_enabled"] = properties["isSftpEnabled"]

        return translated_resounrce


def convert_present_to_raw_storage_accounts(
    hub,
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
    custom_domain: Dict[str, Any] = None,
    customer_managed_key: Dict[str, Any] = None,
    identity: Dict[str, Any] = None,
    network_rules: Dict[str, Any] = None,
    large_file_shares_state: str = None,
    azure_files_authentication: Dict[str, Any] = None,
    routing: Dict[str, Any] = None,
    encryption_service: Dict[str, Any] = None,
    require_infrastructure_encryption: bool = None,
    immutability_policy: Dict[str, Any] = None,
    sas_policy: Dict[str, Any] = None,
    allowed_copy_scope: str = None,
    sftp_enabled: bool = None,
    tags: Dict[str, str] = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location: Specifies the supported Azure location where the resource exists.
         sku_tier: The SKU name
         sku_name: The SKU tier
         account_kind: Defines the Kind of account.
         cross_tenant_replication_enabled: Allow or disallow cross AAD tenant object replication
         access_tier: Required for storage accounts where kind = BlobStorage. The access tier is used for billing
         edge_zone: Specifies the Edge Zone within the Azure Region where this Storage Account should exist.
         enable_https_traffic_only: Boolean flag which forces HTTPS if enabled.
         min_tls_version: The minimum supported TLS version for the storage account.
         allow_blob_public_access:  Allow or disallow nested items within this Account to opt into being public.
         allow_shared_key_access: Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key.
         public_network_access: Whether the public network access is enabled
         default_to_oauth_authentication: Default to Azure Active Directory authorization in the Azure portal when accessing the Storage Account.
         is_hns_enabled: Account HierarchicalNamespace enabled if sets to true.
         nfsv3_enabled: NFS 3.0 protocol support enabled if set to true.
         custom_domain: User domain assigned to the storage account.
         customer_managed_key: Combination of Key vault key id and user assigned id
         identity: The identity of the resource.
         network_rules: Network rule set
         large_file_shares_state: Allow large file shares if sets to enabled.
         azure_files_authentication: Provides the identity based authentication settings for Azure Files.
         routing: Maintains information about the network routing choice opted by the user for data transfer
         encryption_service: set of encryption services
         require_infrastructure_encryption: A boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest.
         immutability_policy: This argument specifies the default account-level immutability policy which is inherited and applied to objects
         sas_policy: SasPolicy assigned to the storage account.
         allowed_copy_scope: Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet.
         sftp_enabled: Enables Secure File Transfer Protocol, if set to true
         tags: Gets or sets a list of key value pairs that describe the resource.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location}

    if tags is not None:
        payload["tags"] = tags

    if (sku_name is not None) or (sku_tier is not None):
        payload["sku"] = {}
    if sku_name is not None:
        payload["sku"]["name"] = sku_name
    if sku_tier is not None:
        payload["sku"]["tier"] = sku_tier

    if account_kind is not None:
        payload["kind"] = account_kind

    if edge_zone is not None:
        payload["extendedLocation"] = {}
        payload["extendedLocation"]["name"] = edge_zone

    if identity is not None:
        payload["identity"] = convert_present_to_raw_identity(hub, identity=identity)

    if (
        (cross_tenant_replication_enabled is not None)
        or (access_tier is not None)
        or (enable_https_traffic_only is not None)
        or (min_tls_version is not None)
        or (allow_blob_public_access is not None)
        or (allow_shared_key_access is not None)
        or (public_network_access is not None)
        or (default_to_oauth_authentication is not None)
        or (is_hns_enabled is not None)
        or (nfsv3_enabled is not None)
        or (custom_domain is not None)
        or (customer_managed_key is not None)
        or (network_rules is not None)
        or (large_file_shares_state is not None)
        or (azure_files_authentication is not None)
        or (routing is not None)
        or (encryption_service is not None)
        or (require_infrastructure_encryption is not None)
        or (immutability_policy is not None)
        or (sas_policy is not None)
        or (allowed_copy_scope is not None)
        or (sftp_enabled is not None)
    ):
        payload["properties"] = {}
    if cross_tenant_replication_enabled is not None:
        payload["properties"][
            "allowCrossTenantReplication"
        ] = cross_tenant_replication_enabled

    if access_tier is not None:
        payload["properties"]["accessTier"] = access_tier

    if enable_https_traffic_only is not None:
        payload["properties"]["supportsHttpsTrafficOnly"] = enable_https_traffic_only

    if min_tls_version is not None:
        payload["properties"]["minimumTlsVersion"] = min_tls_version

    if allow_blob_public_access is not None:
        payload["properties"]["allowBlobPublicAccess"] = allow_blob_public_access

    if allow_shared_key_access is not None:
        payload["properties"]["allowSharedKeyAccess"] = allow_shared_key_access

    if public_network_access is not None:
        payload["properties"]["publicNetworkAccess"] = public_network_access

    if default_to_oauth_authentication is not None:
        payload["properties"][
            "defaultToOAuthAuthentication"
        ] = default_to_oauth_authentication

    if is_hns_enabled is not None:
        payload["properties"]["isHnsEnabled"] = is_hns_enabled

    if nfsv3_enabled is not None:
        payload["properties"]["isNfsV3Enabled"] = nfsv3_enabled

    if custom_domain is not None:
        payload["properties"]["customDomain"] = convert_present_to_raw_custom_domain(
            hub, c_domain=custom_domain
        )

    if (
        (customer_managed_key is not None)
        or (encryption_service is not None)
        or (require_infrastructure_encryption is not None)
    ):
        payload["properties"]["encryption"] = {}

    if customer_managed_key is not None:
        payload["properties"]["encryption"]["keyvaultproperties"] = {}
        payload["properties"]["encryption"]["keyvaultproperties"][
            "currentVersionedKeyIdentifier"
        ] = customer_managed_key["key_vault_key_id"]

        payload["properties"]["encryption"]["identity"] = {}
        payload["properties"]["encryption"]["identity"][
            "userAssignedIdentity"
        ] = customer_managed_key["user_assigned_identity_id"]

    if network_rules is not None:
        payload["properties"]["networkAcls"] = convert_present_to_raw_network_rules(
            hub, rules=network_rules
        )

    if large_file_shares_state is not None:
        payload["properties"]["largeFileSharesState"] = large_file_shares_state

    if azure_files_authentication is not None:
        payload["properties"][
            "azureFilesIdentityBasedAuthentication"
        ] = convert_present_to_raw_files_authentication(
            hub, file_auth=azure_files_authentication
        )

    if routing is not None:
        payload["properties"]["routingPreference"] = convert_present_to_raw_routing(
            hub, routing_pref=routing
        )

    if encryption_service is not None:
        payload["properties"]["encryption"]["keySource"] = encryption_service[
            "encryption_key_source"
        ]
        if (encryption_service.get("queue_encryption_key_type") is not None) or (
            encryption_service.get("table_encryption_key_type") is not None
        ):
            payload["properties"]["encryption"]["services"] = {}

        if encryption_service.get("queue_encryption_key_type") is not None:
            payload["properties"]["encryption"]["services"]["queue"] = {}
            payload["properties"]["encryption"]["services"]["queue"][
                "keyType"
            ] = encryption_service.get("queue_encryption_key_type")

        if encryption_service.get("table_encryption_key_type") is not None:
            payload["properties"]["encryption"]["services"]["table"] = {}
            payload["properties"]["encryption"]["services"]["table"][
                "keyType"
            ] = encryption_service.get("table_encryption_key_type")

    if require_infrastructure_encryption is not None:
        payload["properties"]["encryption"][
            "requireInfrastructureEncryption"
        ] = require_infrastructure_encryption

    if immutability_policy is not None:
        payload["properties"]["immutableStorageWithVersioning"] = {}
        payload["properties"]["immutableStorageWithVersioning"][
            "immutabilityPolicy"
        ] = convert_present_to_raw_immutability_policy(
            hub, immute_policy=immutability_policy
        )

    if sas_policy is not None:
        payload["properties"]["sasPolicy"] = convert_present_to_raw_sas_policy(
            hub, policy=sas_policy
        )

    if allowed_copy_scope is not None:
        payload["properties"]["allowedCopyScope"] = allowed_copy_scope

    if sftp_enabled is not None:
        payload["properties"]["isSftpEnabled"] = sftp_enabled

    return payload


def update_storage_accounts_payload(
    hub, existing_payload: Dict[str, Any], new_values: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
     PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        existing_payload: An existing resource state from Azure. This is usually a GET operation response.
        new_values: A dictionary of desired state values. If any property's value is None,
         this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
         do an update.

    Returns:
        A result dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages tuple.
    """
    result = {"result": True, "ret": None, "comment": []}
    need_update = False
    new_payload = copy.deepcopy(existing_payload)

    if (
        (new_values.get("sku_tier") is not None)
        and (existing_payload.get("sku") is not None)
        and (new_values["sku_tier"] != existing_payload.get("sku").get("tier"))
    ):
        new_payload["sku"]["tier"] = new_values.get("sku_tier")
        need_update = True

    if (
        (new_values.get("sku_name") is not None)
        and (existing_payload.get("sku") is not None)
        and (new_values["sku_name"] != existing_payload.get("sku").get("name"))
    ):
        new_payload["sku"]["name"] = new_values.get("sku_name")
        need_update = True

    if (new_values.get("account_kind") is not None) and (
        new_values["account_kind"] != existing_payload.get("kind")
    ):
        new_payload["kind"] = new_values.get("account_kind")
        need_update = True

    if (
        (new_values.get("cross_tenant_replication_enabled") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["cross_tenant_replication_enabled"]
            != existing_payload.get("properties").get("allowCrossTenantReplication")
        )
    ):
        new_payload["properties"]["allowCrossTenantReplication"] = new_values.get(
            "cross_tenant_replication_enabled"
        )
        need_update = True

    if (
        (new_values.get("access_tier") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["access_tier"]
            != existing_payload.get("properties").get("accessTier")
        )
    ):
        new_payload["properties"]["accessTier"] = new_values.get("access_tier")
        need_update = True

    if (
        (new_values.get("edge_zone") is not None)
        and (existing_payload.get("extendedLocation") is not None)
        and (
            new_values["edge_zone"]
            != existing_payload.get("extendedLocation").get("name")
        )
    ):
        new_payload["extendedLocation"]["type"] = new_values.get("edge_zone")
        need_update = True

    if (
        (new_values.get("enable_https_traffic_only") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["enable_https_traffic_only"]
            != existing_payload.get("properties").get("supportsHttpsTrafficOnly")
        )
    ):
        new_payload["properties"]["supportsHttpsTrafficOnly"] = new_values.get(
            "enable_https_traffic_only"
        )
        need_update = True

    if (
        (new_values.get("min_tls_version") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["min_tls_version"]
            != existing_payload.get("properties").get("minimumTlsVersion")
        )
    ):
        new_payload["properties"]["minimumTlsVersion"] = new_values.get(
            "min_tls_version"
        )
        need_update = True

    if (
        (new_values.get("allow_blob_public_access") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["allow_blob_public_access"]
            != existing_payload.get("properties").get("allowBlobPublicAccess")
        )
    ):
        new_payload["properties"]["allowBlobPublicAccess"] = new_values.get(
            "allow_blob_public_access"
        )
        need_update = True

    if (
        (new_values.get("allow_shared_key_access") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["allow_shared_key_access"]
            != existing_payload.get("properties").get("allowSharedKeyAccess")
        )
    ):
        new_payload["properties"]["allowSharedKeyAccess"] = new_values.get(
            "allow_shared_key_access"
        )
        need_update = True

    if (
        (new_values.get("public_network_access") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["public_network_access"]
            != existing_payload.get("properties").get("publicNetworkAccess")
        )
    ):
        new_payload["properties"]["publicNetworkAccess"] = new_values.get(
            "public_network_access"
        )
        need_update = True

    if (
        (new_values.get("default_to_oauth_authentication") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["default_to_oauth_authentication"]
            != existing_payload.get("properties").get("defaultToOAuthAuthentication")
        )
    ):
        new_payload["properties"]["defaultToOAuthAuthentication"] = new_values.get(
            "default_to_oauth_authentication"
        )
        need_update = True

    if (
        (new_values.get("is_hns_enabled") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["is_hns_enabled"]
            != existing_payload.get("properties").get("isHnsEnabled")
        )
    ):
        new_payload["properties"]["isHnsEnabled"] = new_values.get("is_hns_enabled")
        need_update = True

    if (
        (new_values.get("nfsv3_enabled") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["nfsv3_enabled"]
            != existing_payload.get("properties").get("isNfsV3Enabled")
        )
    ):
        new_payload["properties"]["isNfsV3Enabled"] = new_values.get("nfsv3_enabled")
        need_update = True

    if (new_values.get("custom_domain") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_custom_domain = existing_payload.get("properties").get("customDomain")
        existing_custom_domain_required_payload = convert_raw_to_present_custom_domain(
            hub, c_domain=existing_custom_domain
        )
        if compare_update_dict_payload(
            existing_custom_domain_required_payload, new_values.get("custom_domain")
        ):
            new_payload["properties"][
                "customDomain"
            ] = convert_present_to_raw_custom_domain(
                hub, c_domain=new_values.get("custom_domain")
            )
            need_update = True
    if (new_values.get("customer_managed_key") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_customer_managed_key = existing_payload.get("properties").get(
            "encryption"
        )
        existing_customer_managed_key_required_payload = (
            convert_raw_to_present_customer_managed_key(
                hub, customer_key=existing_customer_managed_key
            )
        )
        if compare_update_dict_payload(
            existing_customer_managed_key_required_payload,
            new_values.get("customer_managed_key"),
        ):
            new_payload["properties"]["encryption"]["identity"][
                "userAssignedIdentity"
            ] = new_values.get("customer_managed_key").get("user_assigned_identity_id")
            new_payload["properties"]["encryption"]["keyvaultproperties"][
                "currentVersionedKeyIdentifier"
            ] = new_values.get("customer_managed_key").get("key_vault_key_id")
            need_update = True

    if new_values.get("identity") is not None:
        existing_identity = existing_payload.get("identity")
        existing_identity_required_payload = convert_raw_to_present_identity(
            hub, identity=existing_identity
        )
        if compare_update_dict_payload(
            existing_identity_required_payload, new_values.get("identity")
        ):
            new_payload["identity"] = convert_present_to_raw_identity(
                hub, identity=new_values.get("identity")
            )
            need_update = True

    if (new_values.get("network_rules") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_network_rules = existing_payload.get("properties").get("networkAcls")
        existing_network_rules_required_payload = convert_raw_to_present_network_rules(
            hub, rules=existing_network_rules
        )
        if compare_update_dict_payload(
            existing_network_rules_required_payload, new_values.get("network_rules")
        ):
            new_payload["properties"][
                "networkAcls"
            ] = convert_present_to_raw_network_rules(
                hub, rules=new_values.get("network_rules")
            )
            need_update = True

    if (
        (new_values.get("large_file_shares_state") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["large_file_shares_state"]
            != existing_payload.get("properties").get("largeFileSharesState")
        )
    ):
        new_payload["properties"]["largeFileSharesState"] = new_values.get(
            "large_file_shares_state"
        )
        need_update = True

    if (new_values.get("azure_files_authentication") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_files_authentication = existing_payload.get("properties").get(
            "azureFilesIdentityBasedAuthentication"
        )
        existing_files_authentication_required_payload = (
            convert_raw_to_present_files_authentication(
                hub, file_auth=existing_files_authentication
            )
        )
        if compare_update_dict_payload(
            existing_files_authentication_required_payload,
            new_values.get("azure_files_authentication"),
        ):
            new_payload["properties"][
                "azureFilesIdentityBasedAuthentication"
            ] = convert_present_to_raw_files_authentication(
                hub, file_auth=new_values.get("azure_files_authentication")
            )
            need_update = True

    if (new_values.get("routing") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_routing = existing_payload.get("properties").get("routingPreference")
        existing_routing_required_payload = convert_raw_to_present_routing(
            hub, routing_pref=existing_routing
        )
        if compare_update_dict_payload(
            existing_routing_required_payload, new_values.get("routing")
        ):
            new_payload["properties"][
                "routingPreference"
            ] = convert_present_to_raw_routing(
                hub, routing_pref=new_values.get("routing")
            )
            need_update = True

    if (new_values.get("encryption_service") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_encryption_service = existing_payload.get("properties").get(
            "encryption"
        )
        existing_encryption_service_required_payload = (
            convert_raw_to_present_encryption_service(
                hub, encryption_service=existing_encryption_service
            )
        )
        if compare_update_dict_payload(
            existing_encryption_service_required_payload,
            new_values.get("encryption_service"),
        ):
            new_payload["properties"]["encryption"]["keySource"] = new_values.get(
                "encryption_service"
            ).get("encryption_key_source")
            if (
                existing_payload.get("properties").get("encryption").get("services")
                is not None
            ):
                if (
                    existing_payload.get("properties")
                    .get("encryption")
                    .get("services")
                    .get("queue")
                    is not None
                ):
                    new_payload["properties"]["encryption"]["services"]["queue"][
                        "keyType"
                    ] = new_values.get("encryption_service").get(
                        "queue_encryption_key_type"
                    )
                if (
                    existing_payload.get("properties")
                    .get("encryption")
                    .get("services")
                    .get("table")
                    is not None
                ):
                    new_payload["properties"]["encryption"]["services"]["table"][
                        "keyType"
                    ] = new_values.get("encryption_service").get(
                        "table_encryption_key_type"
                    )
            need_update = True

    if (
        (new_values.get("require_infrastructure_encryption") is not None)
        and (existing_payload.get("properties") is not None)
        and (existing_payload.get("properties").get("encryption") is not None)
        and (
            new_values["require_infrastructure_encryption"]
            != existing_payload.get("properties")
            .get("encryption")
            .get("requireInfrastructureEncryption")
        )
    ):
        new_payload["properties"]["encryption"][
            "requireInfrastructureEncryption"
        ] = new_values.get("require_infrastructure_encryption")
        need_update = True

    if (
        (new_values.get("immutability_policy") is not None)
        and (existing_payload.get("properties") is not None)
        and (existing_payload.get("immutableStorageWithVersioning") is not None)
    ):
        existing_immutability_policy = (
            existing_payload.get("properties")
            .get("immutableStorageWithVersioning")
            .get("immutabilityPolicy")
        )
        existing_immutability_policy_required_payload = (
            convert_raw_to_present_immutability_policy(
                hub, immute_policy=existing_immutability_policy
            )
        )
        if compare_update_dict_payload(
            existing_immutability_policy_required_payload,
            new_values.get("immutability_policy"),
        ):
            new_payload["properties"]["immutableStorageWithVersioning"][
                "immutabilityPolicy"
            ] = convert_present_to_raw_immutability_policy(
                hub, immute_policy=new_values.get("immutability_policy")
            )
            need_update = True

    if (new_values.get("sas_policy") is not None) and (
        existing_payload.get("properties") is not None
    ):
        existing_sas_policy = existing_payload.get("properties").get(".sasPolicy")
        existing_sas_policy_required_payload = convert_raw_to_present_sas_policy(
            hub, policy=existing_sas_policy
        )
        if compare_update_dict_payload(
            existing_sas_policy_required_payload, new_values.get("sas_policy")
        ):
            new_payload["properties"]["sasPolicy"] = convert_present_to_raw_sas_policy(
                hub, policy=new_values.get("sas_policy")
            )
            need_update = True

    if (
        (new_values.get("allowed_copy_scope") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["allowed_copy_scope"]
            != existing_payload.get("properties").get("allowedCopyScope")
        )
    ):
        new_payload["properties"]["allowedCopyScope"] = new_values.get(
            "allowed_copy_scope"
        )
        need_update = True

    if (
        (new_values.get("sftp_enabled") is not None)
        and (existing_payload.get("properties") is not None)
        and (
            new_values["sftp_enabled"]
            != existing_payload.get("properties").get("isSftpEnabled")
        )
    ):
        new_payload["properties"]["isSftpEnabled"] = new_values.get("sftp_enabled")
        need_update = True

    if (new_values.get("tags") is not None) and (
        new_values["tags"] != existing_payload.get("tags")
    ):
        new_payload["tags"] = new_values.get("tags")
        need_update = True

    if need_update:
        result["ret"] = new_payload
    return result


def compare_update_dict_payload(
    existing_payload: Dict[str, Any], update_payload: Dict[str, Any]
):
    """
    Compares the payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_payload(Dict): Existing payload
        update_payload(Dict): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    for parameter in update_payload:
        if parameter in existing_payload:
            if update_payload.get(parameter) != existing_payload.get(parameter):
                return True
        else:
            return True
    return False


def convert_raw_to_present_custom_domain(hub, c_domain: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        c_domain(Dict, optional): Custom Disk payload in a storage account resource.

    Returns:
         Custom Domain payload that contains the parameters that match respective present function's input format.
    """
    custom_domain_payload = {
        "name": c_domain.get("name"),
    }
    if c_domain.get("useSubDomainName") is not None:
        custom_domain_payload["use_subdomain"] = c_domain.get("useSubDomainName")

    return custom_domain_payload


def convert_raw_to_present_customer_managed_key(hub, customer_key: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        customer_key(Dict, optional): customer key payload in a storage account resource.

    Returns:
         customer key payload that contains the parameters that match respective present function's input format.
    """
    customer_key_payload = {}
    if customer_key.get("keyvaultproperties") and customer_key.get(
        "keyvaultproperties"
    ).get("currentVersionedKeyIdentifier"):
        customer_key_payload["key_vault_key_id"] = customer_key.get(
            "keyvaultproperties"
        ).get("currentVersionedKeyIdentifier")

    if customer_key.get("identity") and customer_key.get("identity").get(
        "userAssignedIdentity"
    ):
        customer_key_payload["user_assigned_identity_id"] = customer_key.get(
            "identity"
        ).get("userAssignedIdentity")

    return customer_key_payload


def convert_raw_to_present_identity(hub, identity: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        identity(Dict, optional): Identity payload in a storage account resource.

    Returns:
         Identity payload that contains the parameters that match respective present function's input format.
    """
    identity_payload = {
        "type": identity.get("type"),
    }
    if identity.get("userAssignedIdentities") is not None:
        identity_payload["user_assigned_identities"] = identity.get(
            "userAssignedIdentities"
        ).copy()

    return identity_payload


def convert_raw_to_present_sas_policy(hub, policy: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        policy(Dict, optional): sas policy payload in a storage account resource.

    Returns:
         sas policy payload that contains the parameters that match respective present function's input format.
    """
    sas_policy_payload = {
        "expiration_period": policy.get["sasExpirationPeriod"],
    }
    if policy.get("expirationAction") is not None:
        sas_policy_payload["expiration_action"] = policy["expirationAction"]

    return sas_policy_payload


def convert_raw_to_present_immutability_policy(hub, immutePolicy: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

     Args:
         immutePolicy(Dict, optional): immutability policy payload in a storage account resource.

    Returns:
        immutability policy payload that contains the parameters that match respective present function's input format.
    """
    immutability_policy_payload = {
        "allow_protected_append_writes": immutePolicy["allowProtectedAppendWrites"],
        "state": immutePolicy["state"],
        "period_since_creation_in_days": immutePolicy[
            "immutabilityPeriodSinceCreationInDays"
        ],
    }
    return immutability_policy_payload


def convert_raw_to_present_routing(hub, routing_pref: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

     Args:
         routing_pref(Dict, optional): routing payload in a storage account resource.

    Returns:
        routing payload that contains the parameters that match respective present function's input format.
    """
    routing_payload = {}

    if routing_pref.get("publishInternetEndpoints") is not None:
        routing_payload["publish_internet_endpoints"] = routing_pref[
            "publishInternetEndpoints"
        ]

    if routing_pref.get("publishMicrosoftEndpoints") is not None:
        routing_payload["publish_microsoft_endpoints"] = routing_pref[
            "publishMicrosoftEndpoints"
        ]

    if routing_pref.get("routingChoice") is not None:
        routing_payload["routing_choice"] = routing_pref["routingChoice"]
    return routing_payload


def convert_raw_to_present_encryption_service(hub, encryption_service: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        encryption_service(Dict, optional): encryption service payload in a storage account resource.

    Returns:
         encryption service payload that contains the parameters that match respective present function's input format.
    """
    encryption_service_payload = {}
    if encryption_service.get("keySource"):
        encryption_service_payload["encryption_key_source"] = encryption_service.get(
            "keySource"
        )

    if (
        (encryption_service.get("services"))
        and (encryption_service.get("services").get("queue"))
        and (encryption_service.get("services").get("queue").get("keyType"))
    ):
        encryption_service["queue_encryption_key_type"] = (
            encryption_service.get("services").get("queue").get("keyType")
        )

    if (
        (encryption_service.get("services"))
        and (encryption_service.get("services").get("table"))
        and (encryption_service.get("services").get("table").get("keyType"))
    ):
        encryption_service["table_encryption_key_type"] = (
            encryption_service.get("services").get("table").get("keyType")
        )

    return encryption_service_payload


def convert_raw_to_present_files_authentication(hub, file_auth: Dict[str, Any]):
    """
    Giving an existing resource state and desired state inputs, generate a Dict that match the format of
    present input parameters.

    Args:
        file_auth(Dict, optional): file authentication payload in a storage account resource.

    Returns:
        file authentication payload that contains the parameters that match respective present function's input format.
    """
    files_authentication_payload = {
        "directory_service_options": file_auth["directoryServiceOptions"],
    }

    if file_auth.get("activeDirectoryProperties") is not None:
        active_directory_payload = covert_raw_to_present_active_directory(
            hub, directory_properties=file_auth.get("activeDirectoryProperties")
        )
        files_authentication_payload[
            "active_directory_properties"
        ] = active_directory_payload
    return files_authentication_payload


def covert_raw_to_present_active_directory(hub, directory_properties: Dict[str, Any]):
    current_directory_payload = {
        "azure_storage_sid": directory_properties["azureStorageSid"],
        "domain_name": directory_properties["domainName"],
        "domain_sid": directory_properties["domainSid"],
        "domain_guid": directory_properties["domainGuid"],
        "forest_name": directory_properties["forestName"],
        "netbios_domain_name": directory_properties["netBiosDomainName"],
    }
    return current_directory_payload


def convert_raw_to_present_network_rules(hub, rules: Dict[str, Any]):
    """
    Giving an existing resource state and desired state inputs, generate a Dict that match the format of
    present input parameters.

    Args:
        rules(Dict, optional): network rules payload in a storage account resource.

    Returns:
       network rules payload that contains the parameters that match respective present function's input format.
    """
    network_rule_payload = {
        "default_action": rules["defaultAction"],
    }
    if rules.get("bypass") is not None:
        network_rule_payload["bypass"] = rules["bypass"]

    if rules.get("ipRules") is not None:
        ip = []
        for ip_rule in rules["ipRules"]:
            ip.append(ip_rule.get("value"))
        network_rule_payload["ip_rule_values"] = ip

    if rules.get("virtualNetworkRules") is not None:
        subnetIds = []
        for vnRules in rules["virtualNetworkRules"]:
            subnetIds.append(vnRules.get("id"))
        network_rule_payload["virtual_network_subnet_ids"] = subnetIds

    if rules.get("resourceAccessRules") is not None:
        resource_access_rules_payload = convert_raw_to_present_resource_access_rules(
            hub, resource_access=rules.get("resourceAccessRules")
        )
        network_rule_payload["resource_access_rules"] = resource_access_rules_payload

    return network_rule_payload


def convert_raw_to_present_resource_access_rules(
    hub, resource_access: List[Dict[str, Any]]
):
    present_resource_access_rule = []

    for access_rule in resource_access:
        payload = {"endpoint_resource_id": access_rule["resourceId"]}

        if access_rule.get("tenantId") is not None:
            payload["endpoint_tenant_id"] = access_rule["tenantId"]
        present_resource_access_rule.append(payload)

    return present_resource_access_rule


def convert_present_to_raw_custom_domain(hub, c_domain: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        c_domain(Dict(str, Any)) :

    Returns:
        Custom Domain Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    custom_domain_payload = {
        "name": c_domain.get("name"),
    }

    if c_domain.get("use_subdomain"):
        custom_domain_payload["useSubDomainName"] = c_domain["use_subdomain"]

    return custom_domain_payload


def convert_present_to_raw_identity(hub, identity: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        identity(Dict(str, Any)) :

    Returns:
        identity Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    identity_payload = {
        "type": identity.get("type"),
    }

    if identity.get("user_assigned_identities"):
        identity_payload["userAssignedIdentities"] = identity.get(
            "user_assigned_identities"
        ).copy()

        return identity_payload


def convert_present_to_raw_sas_policy(hub, policy: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        policy(Dict(str, Any)) :

    Returns:
        Sas Policy Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    sas_policy_payload = {
        "sasExpirationPeriod": policy.get("expiration_period"),
    }

    if policy.get("expiration_action"):
        sas_policy_payload["expirationAction"] = policy["expiration_action"]

    return sas_policy_payload


def convert_present_to_raw_immutability_policy(hub, immute_policy: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        immute_policy(Dict(str, Any)) :

    Returns:
        Immutability Policy Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    immutability_policy_payload = {
        "allowProtectedAppendWrites": immute_policy["allow_protected_append_writes"],
        "state": immute_policy["state"],
        "immutabilityPeriodSinceCreationInDays": immute_policy[
            "period_since_creation_in_days"
        ],
    }
    return immutability_policy_payload


def convert_present_to_raw_routing(hub, routing_pref: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        routing_pref(Dict(str, Any)) :

    Returns:
        Routing Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    routing_payload = {}

    if routing_pref.get("publish_internet_endpoints"):
        routing_payload["publishInternetEndpoints"] = routing_pref[
            "publish_internet_endpoints"
        ]

    if routing_pref.get("publish_microsoft_endpoints"):
        routing_payload["publishMicrosoftEndpoints"] = routing_pref[
            "publish_microsoft_endpoints"
        ]

    if routing_pref.get("routing_choice"):
        routing_payload["routingChoice"] = routing_pref["routing_choice"]
    return routing_payload


def convert_present_to_raw_files_authentication(hub, file_auth: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
       file_auth(Dict(str, Any)) :

    Returns:
        file authentication Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    files_authentication_payload = {
        "directoryServiceOptions": file_auth["directory_service_options"],
    }

    if file_auth.get("active_directory_properties"):
        files_authentication_payload[
            "activeDirectoryProperties"
        ] = convert_present_to_raw_active_directory(
            hub, directory_properties=file_auth.get("active_directory_properties")
        )
    return files_authentication_payload


def convert_present_to_raw_active_directory(hub, directory_properties: Dict[str, Any]):
    current_directory_payload = {
        "azureStorageSid": directory_properties["azure_storage_sid"],
        "domainName": directory_properties["domain_name"],
        "domainSid": directory_properties["domain_sid"],
        "domainGuid": directory_properties["domain_guid"],
        "forestName": directory_properties["forest_name"],
        "netBiosDomainName": directory_properties["netbios_domain_name"],
    }
    return current_directory_payload


def convert_present_to_raw_network_rules(hub, rules: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
       rules(Dict(str, Any)) :

    Returns:
       Network rules Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    network_rule_payload = {
        "defaultAction": rules["default_action"],
    }

    if rules.get("bypass"):
        network_rule_payload["bypass"] = rules["bypass"]

    if rules.get("ip_rule_values"):
        ipRuleList = []
        for value in rules["ip_rule_values"]:
            ipRuleList.append({"action": "Allow", "value": value})
        network_rule_payload["ipRules"] = ipRuleList

    if rules.get("virtual_network_subnet_ids"):
        virtualNetworkRuleList = []
        for id in rules["virtual_network_subnet_ids"]:
            virtualNetworkRuleList.append(
                {"action": "Allow", "id": id, "state": "Succeeded"}
            )
        network_rule_payload["virtualNetworkRules"] = virtualNetworkRuleList

    if rules.get("resource_access_rules"):
        network_rule_payload[
            "resourceAccessRules"
        ] = convert_present_to_raw_resource_access_rules(
            hub, resource_access=rules.get("resource_access_rules")
        )

    return network_rule_payload


def convert_present_to_raw_resource_access_rules(
    hub, resource_access: List[Dict[str, Any]]
):
    raw_access_rules = []

    for access_rule in resource_access:
        payload = {
            "resourceId": access_rule["endpoint_resource_id"],
        }
        if access_rule.get("endpoint_tenant_id"):
            payload["tenantId"] = access_rule["endpoint_tenant_id"]
        raw_access_rules.append(payload)

    return raw_access_rules
