import copy
from typing import Any
from typing import Dict


def convert_raw_log_analytics_workspace_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    workspace_name: str,
    resource_id: str,
    subscription_id: str,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a dict that match the format of
     present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        workspace_name: Azure Workspace resource name.
        resource_id: Azure Log Analytics Workspace resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
        A dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "workspace_name": workspace_name,
        "location": resource["location"],
        "subscription_id": subscription_id,
    }
    if "tags" in resource:
        resource_translated["tags"] = resource["tags"]
    properties = resource.get("properties")
    if properties:
        properties_parameters = {
            "retentionInDays": "retention_in_days",
            "publicNetworkAccessForIngestion": "public_network_access_for_ingestion",
            "publicNetworkAccessForQuery": "public_network_access_for_query",
        }
        for parameter_raw, parameter_present in properties_parameters.items():
            if parameter_raw in properties:
                resource_translated[parameter_present] = properties.get(parameter_raw)

        if properties.get("features") is not None:
            existing_features_required_payload = convert_raw_features_to_present(
                features=properties["features"]
            )
            resource_translated["features"] = existing_features_required_payload
        if properties.get("sku") is not None:
            existing_sku_required_payload = convert_raw_sku_to_present(
                sku=properties["sku"]
            )
            resource_translated["sku"] = existing_sku_required_payload
        if properties.get("workspaceCapping") is not None:
            existing_workspace_capping_required_payload = (
                convert_raw_workspace_capping_to_present(
                    workspace_capping=properties["workspaceCapping"]
                )
            )
            resource_translated[
                "workspace_capping"
            ] = existing_workspace_capping_required_payload
    return resource_translated


def convert_present_log_analytics_workspace_to_raw(
    hub,
    subscription_id: str,
    public_network_access_for_query: str = None,
    public_network_access_for_ingestion: str = None,
    retention_in_days: int = None,
    workspace_capping: Dict = None,
    features: Dict = None,
    sku: Dict = None,
    location: str = None,
    tags: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        subscription_id: subscription id
        public_network_access_for_query: The network access type for accessing Log Analytics query.
        public_network_access_for_ingestion: The network access type for accessing Log Analytics ingestion.
        retention_in_days: The workspace data retention in days. Allowed values are per pricing plan.
        workspace_capping(dict, optional): The daily volume cap for ingestion.
        features(list[dict], optional): Workspace features.
        sku(dict, optional): The SKU of the workspace.
        location: Resource location. This field can not be updated.
        tags: Resource tags.

    Returns:
        A dict in the format of an Azure PUT operation payload.
    """
    payload = {"location": location, "properties": {}}
    if tags is not None:
        payload["tags"] = tags
    if retention_in_days is not None:
        payload["properties"]["retentionInDays"] = retention_in_days
    if public_network_access_for_ingestion is not None:
        payload["properties"][
            "publicNetworkAccessForIngestion"
        ] = public_network_access_for_ingestion
    if public_network_access_for_query is not None:
        payload["properties"][
            "publicNetworkAccessForQuery"
        ] = public_network_access_for_query
    if sku is not None:
        sku_payload = convert_present_sku_to_raw(sku)
        payload["properties"]["sku"] = sku_payload
    if features is not None:
        features_payload = convert_present_features_to_raw(features)
        payload["properties"]["features"] = features_payload
    if workspace_capping is not None:
        workspace_capping_payload = convert_present_workspace_capping_to_raw(
            workspace_capping
        )
        payload["properties"]["workspaceCapping"] = workspace_capping_payload
    return payload


def update_log_analytics_workspace_payload(
    hub,
    subscription_id: str,
    existing_payload: Dict[str, Any],
    new_values: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate an updated payload, which can be used by
     PUT operation to update a resource on Azure.

    Args:
        hub: The redistributed pop central hub.
        subscription_id: subscription id required to update network security group for VN subnet
        existing_payload: An existing resource state from Azure. This is usually a GET operation response.
        new_values: A dictionary of desired state values. If any property's value is None,
         this property will be ignored. This is to match the behavior when a present() input is a None, Idem does not
         do an update.

    Returns:
        A result dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    is_updated = False
    new_payload = copy.deepcopy(existing_payload)
    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values["tags"]
        is_updated = True
    existing_properties = existing_payload["properties"]
    if (new_values.get("retention_in_days") is not None) and (
        new_values["retention_in_days"] != existing_properties.get("retentionInDays")
    ):
        new_payload["properties"]["retentionInDays"] = new_values.get(
            "retention_in_days"
        )
        is_updated = True
    if (new_values.get("public_network_access_for_ingestion") is not None) and (
        new_values["public_network_access_for_ingestion"]
        != existing_properties.get("publicNetworkAccessForIngestion")
    ):
        new_payload["properties"]["publicNetworkAccessForIngestion"] = new_values.get(
            "public_network_access_for_ingestion"
        )
        is_updated = True
    if (new_values.get("public_network_access_for_query") is not None) and (
        new_values["public_network_access_for_query"]
        != existing_properties.get("publicNetworkAccessForQuery")
    ):
        new_payload["properties"]["publicNetworkAccessForQuery"] = new_values.get(
            "public_network_access_for_query"
        )
        is_updated = True
    if (new_values.get("sku") is not None) and (
        compare_accurate_object(
            new_values.get("sku"),
            convert_raw_sku_to_present(existing_properties["sku"]),
        )
    ):
        new_payload["properties"]["sku"] = convert_present_sku_to_raw(new_values["sku"])
        is_updated = True
    if (new_values.get("features") is not None) and compare_accurate_object(
        new_values.get("features"),
        convert_raw_features_to_present(existing_properties["features"]),
    ):
        new_payload["properties"]["features"] = convert_present_features_to_raw(
            new_values.get("features")
        )
        is_updated = True
    if (new_values.get("workspace_capping") is not None) and compare_accurate_object(
        new_values.get("features"),
        convert_raw_workspace_capping_to_present(
            existing_properties.get("workspaceCapping")
        ),
    ):
        new_payload["properties"][
            "workspaceCapping"
        ] = convert_present_workspace_capping_to_raw(
            new_values.get("workspace_capping")
        )
        is_updated = True
    if is_updated:
        result["ret"] = new_payload
    return result


def convert_present_features_to_raw(features: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        features(Dict[str, Any]) : Feature for Log Analytics creation

    Returns:
        Features payload : Dict[str,any] in the format of an Azure PUT operation payload.
    """
    features_payload = {}
    if features.get("enable_log_access_using_only_resource_permissions") is not None:
        features_payload["enableLogAccessUsingOnlyResourcePermissions"] = features.get(
            "enable_log_access_using_only_resource_permissions"
        )
    if features.get("legacy") is not None:
        features_payload["legacy"] = features.get("legacy")
    if features.get("search_version") is not None:
        features_payload["searchVersion"] = features.get("search_version")
    if features.get("clusterResourceId") is not None:
        features_payload["cluster_resource_id"] = features.get("cluster_resource_id")
    if features.get("enable_data_export") is not None:
        features_payload["enableDataExport"] = features.get("enable_data_export")
    if features.get("disable_local_auth") is not None:
        features_payload["disableLocalAuth"] = features.get("disable_local_auth")
    if features.get("immediate_purge_data_on_30_days") is not None:
        features_payload["immediatePurgeDataOn30Days"] = features.get(
            "immediate_purge_data_on_30_days"
        )

    return features_payload


def convert_raw_features_to_present(features: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        features(Dict, optional): Features payload in a log analytics resource

    Returns:
         Log analytics payload that contains the parameters that match respective present function's input format.
    """
    features_payload = {}
    if features.get("enableLogAccessUsingOnlyResourcePermissions") is not None:
        features_payload[
            "enable_log_access_using_only_resource_permissions"
        ] = features.get("enableLogAccessUsingOnlyResourcePermissions")
    if features.get("legacy") is not None:
        features_payload["legacy"] = features.get("legacy")
    if features.get("searchVersion") is not None:
        features_payload["search_version"] = features.get("searchVersion")
    if features.get("clusterResourceId") is not None:
        features_payload["cluster_resource_id"] = features.get("clusterResourceId")
    if features.get("enableDataExport") is not None:
        features_payload["enable_data_export"] = features.get("enableDataExport")
    if features.get("disableLocalAuth") is not None:
        features_payload["disable_local_auth"] = features.get("disableLocalAuth")
    if features.get("immediatePurgeDataOn30Days") is not None:
        features_payload["immediate_purge_data_on_30_days"] = features.get(
            "immediatePurgeDataOn30Days"
        )

    return features_payload


def convert_present_sku_to_raw(sku: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        sku(Dict[str, Any]) : Feature for Log Analytics creation

    Returns:
        sku payload : Dict[str,any] in the format of an Azure PUT operation payload.
    """
    sku_payload = {}
    if sku.get("capacity_reservation_level") is not None:
        sku_payload["capacityReservationLevel"] = sku.get("capacity_reservation_level")
    if sku.get("last_sku_update") is not None:
        sku_payload["lastSkuUpdate"] = sku.get("last_sku_update")
    if sku.get("name") is not None:
        sku_payload["name"] = sku.get("name")

    return sku_payload


def convert_raw_sku_to_present(sku: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        sku(Dict, optional): Features payload in a log analytics resource

    Returns:
         Log analytics payload that contains the parameters that match respective present function's input format.
    """
    sku_payload = {}
    if sku.get("capacityReservationLevel") is not None:
        sku_payload["capacity_reservation_level"] = sku.get("capacityReservationLevel")
    if sku.get("lastSkuUpdate") is not None:
        sku_payload["last_sku_update"] = sku.get("lastSkuUpdate")
    if sku.get("name") is not None:
        sku_payload["name"] = sku.get("name")

    return sku_payload


def convert_present_workspace_capping_to_raw(workspace_capping: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        workspace_capping(Dict[str, Any]) : Feature for Log Analytics creation

    Returns:
        Features payload : Dict[str,any] in the format of an Azure PUT operation payload.
    """
    workspace_capping_payload = {}
    if workspace_capping.get("daily_quota_gb") is not None:
        workspace_capping_payload["dailyQuotaGb"] = workspace_capping.get(
            "daily_quota_gb"
        )
    if workspace_capping.get("data_ingestion_status") is not None:
        workspace_capping_payload["dataIngestionStatus"] = workspace_capping.get(
            "data_ingestion_status"
        )
    if workspace_capping.get("quota_next_reset_time") is not None:
        workspace_capping_payload["quotaNextResetTime"] = workspace_capping.get(
            "quota_next_reset_time"
        )

    return workspace_capping_payload


def convert_raw_workspace_capping_to_present(workspace_capping: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        workspace_capping(Dict, optional): Features payload in a log analytics resource

    Returns:
         Log analytics payload that contains the parameters that match respective present function's input format.
    """
    workspace_capping_payload = {}
    if workspace_capping.get("dailyQuotaGb") is not None:
        workspace_capping_payload["daily_quota_gb"] = workspace_capping.get(
            "dailyQuotaGb"
        )
    if workspace_capping.get("dataIngestionStatus") is not None:
        workspace_capping_payload["data_ingestion_status"] = workspace_capping.get(
            "dataIngestionStatus"
        )
    if workspace_capping.get("quotaNextResetTime") is not None:
        workspace_capping_payload["quota_next_reset_time"] = workspace_capping.get(
            "quotaNextResetTime"
        )

    return workspace_capping_payload


def compare_accurate_object(
    new_object: Dict[str, Any], existing_object: Dict[str, Any]
):
    is_updated = False
    if len(existing_object) != len(new_object):
        return True
    for existing_key, existing_value in existing_object.items():
        new_value = new_object.get(existing_key)
        if new_value != existing_value:
            is_updated = True

    return is_updated
