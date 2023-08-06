import copy
from typing import Any
from typing import Dict
from typing import List


def convert_present_to_raw_virtual_machine(
    hub,
    location: str,
    virtual_machine_size: str,
    network_interface_ids: List[str],
    storage_image_reference: Dict[str, Any],
    storage_os_disk: Dict[str, Any],
    storage_data_disks: List[Dict[str, Any]],
    os_profile: Dict[str, Any],
    tags: Dict = None,
):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        hub: The redistributed pop central hub.
        location(str): Resource location. Changing this forces a new resource to be created.
        virtual_machine_size(str): Specifies the size of the Virtual Machine.
        network_interface_ids(List[str]): A list of Network Interface IDs which should be associated with the Virtual Machine.
        tags(Dict, optional): Resource tags.
        os_profile(Dict): Specifies the operating system settings used while creating the virtual machine.
        storage_image_reference(Dict): Specifies information about the image to use. Eg- platform images, marketplace images.
        storage_os_disk(Dict): Specifies information about the operating system disk used by the virtual machine.
        storage_data_disks(list(Dict), optional): List of Data disks attached/added to a VM.

    Returns:
        A Dict in the format of an Azure PUT operation payload.
    """
    payload = {
        "location": location,
        "properties": {"hardwareProfile": {"vmSize": virtual_machine_size}},
    }
    if network_interface_ids is not None:
        network_interface_ids_payload = {
            "networkInterfaces": convert_present_to_raw_network_interfaces(
                network_interface_ids
            )
        }
        payload["properties"]["networkProfile"] = network_interface_ids_payload

    storage_profile_payload = {}
    if storage_image_reference is not None:
        storage_profile_payload[
            "imageReference"
        ] = convert_present_to_raw_image_reference(storage_image_reference)
    if storage_os_disk is not None:
        storage_profile_payload["osDisk"] = convert_present_to_raw_os_disk(
            storage_os_disk
        )
    if storage_data_disks is not None:
        storage_profile_payload["dataDisks"] = convert_present_to_raw_data_disks(
            storage_data_disks
        )
    payload["properties"]["storageProfile"] = storage_profile_payload

    if os_profile is not None:
        payload["properties"]["osProfile"] = convert_present_to_raw_os_profile(
            os_profile
        )

    if tags is not None:
        payload["tags"] = tags

    return payload


def convert_raw_virtual_machine_to_present(
    hub,
    resource: Dict,
    idem_resource_name: str,
    resource_group_name: str,
    virtual_machine_name: str,
    resource_id: str,
    subscription_id: str = None,
) -> Dict[str, Any]:
    """
    Giving an existing resource state and desired state inputs, generate a Dict that match the format of
    present input parameters.

    Args:
        hub: The redistributed pop central hub.
        resource: An existing resource state from Azure. This is usually a GET operation response.
        idem_resource_name: The Idem name of the resource.
        resource_group_name: Azure Resource Group name.
        virtual_machine_name: Azure Virtual Machine resource name.
        resource_id: Azure Virtual Machine resource id.
        subscription_id: The Microsoft Azure subscription ID.

    Returns:
      A Dict that contains the parameters that match the present function's input format.
    """
    resource_translated = {
        "name": idem_resource_name,
        "resource_id": resource_id,
        "resource_group_name": resource_group_name,
        "virtual_machine_name": virtual_machine_name,
        "location": resource.get("location"),
        "subscription_id": subscription_id,
    }
    properties = resource.get("properties")
    if properties:
        if properties.get("hardwareProfile") is not None:
            resource_translated["virtual_machine_size"] = properties.get(
                "hardwareProfile"
            ).get("vmSize")
        if properties.get("osProfile") is not None:
            os_profile_payload = convert_raw_to_present_os_profile(
                os_profile=properties.get("osProfile")
            )
            resource_translated["os_profile"] = os_profile_payload

        if properties.get("networkProfile") is not None:
            if properties.get("networkProfile").get("networkInterfaces") is not None:
                network_profile_payload = convert_raw_to_present_network_interface(
                    network_interfaces=properties.get("networkProfile").get(
                        "networkInterfaces"
                    )
                )
                resource_translated["network_interface_ids"] = network_profile_payload

        if properties.get("storageProfile") is not None:
            storage_profile_properties = properties.get("storageProfile")
            if storage_profile_properties.get("imageReference") is not None:
                image_reference_payload = convert_raw_to_present_image_reference(
                    image_reference=storage_profile_properties.get("imageReference")
                )
                resource_translated["storage_image_reference"] = image_reference_payload
            if storage_profile_properties.get("osDisk") is not None:
                os_disk_payload = convert_raw_to_present_os_disk(
                    os_disk=storage_profile_properties.get("osDisk")
                )
                resource_translated["storage_os_disk"] = os_disk_payload
            if storage_profile_properties.get("dataDisks") is not None:
                data_disk_payload = convert_raw_to_present_data_disks(
                    data_disks=storage_profile_properties.get("dataDisks")
                )
                resource_translated["storage_data_disks"] = data_disk_payload
    if "tags" in resource:
        resource_translated["tags"] = resource.get("tags")
    return resource_translated


def update_virtual_machine_payload(
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
        A result Dict.
        result: True if no error occurs during the operation.
        ret: An updated payload that can be used to call PUT operation to update the resource. None if no update on all values.
        comment: A messages list.
    """
    result = {"result": True, "ret": None, "comment": []}
    need_update = False
    new_payload = copy.deepcopy(existing_payload)
    existing_properties = existing_payload.get("properties")

    updated_properties_payload = new_payload.get("properties")
    if new_values.get("virtual_machine_size") is not None:
        if (
            (existing_properties.get("hardwareProfile") is not None)
            and (existing_properties.get("hardwareProfile").get("vmSize") is not None)
            and (
                existing_properties.get("hardwareProfile").get("vmSize")
                != new_values.get("virtual_machine_size")
            )
        ):
            updated_properties_payload["hardwareProfile"]["vmSize"] = new_values.get(
                "virtual_machine_size"
            )
            need_update = True

    if new_values.get("network_interface_ids"):
        if (
            (existing_properties.get("networkProfile") is not None)
            and (
                existing_properties.get("networkProfile").get("networkInterfaces")
                is not None
            )
            and (
                compare_network_interface_payload(
                    existing_properties.get("networkProfile").get("networkInterfaces"),
                    new_values.get("network_interface_ids"),
                )
            )
        ):
            network_profile_payload = {
                "networkInterfaces": convert_present_to_raw_network_interfaces(
                    network_interface_ids=new_values.get("network_interface_ids")
                )
            }
            updated_properties_payload["networkProfile"] = network_profile_payload
            need_update = True
    if new_values.get("storage_data_disks") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (existing_properties.get("storageProfile").get("dataDisks") is not None)
            and (
                compare_storage_data_disks_payload(
                    existing_properties.get("storageProfile").get("dataDisks"),
                    new_values.get("storage_data_disks"),
                )
            )
        ):
            updated_properties_payload["storageProfile"][
                "dataDisks"
            ] = convert_present_to_raw_data_disks(
                data_disks=merge_data_disks_payloads(
                    convert_raw_to_present_data_disks(
                        existing_properties.get("storageProfile").get("dataDisks")
                    ),
                    new_values.get("storage_data_disks"),
                )
            )
            need_update = True
    if new_values.get("storage_os_disk") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (existing_properties.get("storageProfile").get("osDisk") is not None)
            and (
                compare_storage_os_disk_payload(
                    existing_properties.get("storageProfile").get("osDisk"),
                    new_values.get("storage_os_disk"),
                )
            )
        ):
            updated_properties_payload["storageProfile"][
                "osDisk"
            ] = convert_present_to_raw_os_disk(
                os_disk=merge_dictionary_payloads(
                    convert_raw_to_present_os_disk(
                        existing_properties.get("storageProfile").get("osDisk")
                    ),
                    new_values.get("storage_os_disk"),
                )
            )
            need_update = True
    if new_values.get("storage_image_reference") is not None:
        if (
            (existing_properties.get("storageProfile") is not None)
            and (
                existing_properties.get("storageProfile").get("imageReference")
                is not None
            )
            and (
                compare_storage_image_reference_payload(
                    existing_properties.get("storageProfile").get("imageReference"),
                    new_values.get("storage_image_reference"),
                )
            )
        ):
            updated_properties_payload["storageProfile"][
                "imageReference"
            ] = convert_present_to_raw_image_reference(
                storage_image_reference=merge_dictionary_payloads(
                    convert_raw_to_present_image_reference(
                        existing_properties.get("storageProfile").get("imageReference")
                    ),
                    new_values.get("storage_image_reference"),
                )
            )
            need_update = True
    if new_values.get("os_profile") is not None:
        if (existing_properties.get("osProfile") is not None) and (
            compare_os_profile_payload(
                existing_properties.get("osProfile"), new_values.get("os_profile")
            )
        ):
            updated_properties_payload["osProfile"] = convert_present_to_raw_os_profile(
                os_profile=merge_dictionary_payloads(
                    convert_raw_to_present_os_profile(
                        existing_properties.get("osProfile")
                    ),
                    new_values.get("os_profile"),
                )
            )
            need_update = True

    new_payload["properties"] = updated_properties_payload

    if (new_values.get("tags") is not None) and (
        existing_payload.get("tags") != new_values.get("tags")
    ):
        new_payload["tags"] = new_values.get("tags")
        need_update = True

    if need_update:
        result["ret"] = new_payload
    return result


def convert_present_to_raw_network_interfaces(network_interface_ids: List[str]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        network_interface_ids(list(str)) : List of Network Interface Ids

    Returns:
        Network Interface Ids List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    network_interface_id_counter = 0
    network_interfaces_list: List = []
    for network_interface_id in network_interface_ids:
        network_interfaces_payload = {"id": network_interface_id}
        primary_network_payload = {}
        if network_interface_id_counter == 0:
            primary_network_payload["primary"] = True
        else:
            primary_network_payload["primary"] = False
        network_interfaces_payload["properties"] = primary_network_payload
        network_interfaces_list.append(network_interfaces_payload)
        network_interface_id_counter = network_interface_id_counter + 1
    return network_interfaces_list


def convert_present_to_raw_image_reference(storage_image_reference: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        storage_image_reference(Dict(str, Any)) : Specifies information about the image to use in VM creation/update

    Returns:
        Storage Image Reference Dict[str,any] in the format of an Azure PUT operation payload.
    """
    storage_image_reference_payload = {
        "publisher": storage_image_reference.get("image_publisher"),
        "offer": storage_image_reference.get("image_offer"),
        "sku": storage_image_reference.get("image_sku"),
        "version": storage_image_reference.get("image_version"),
    }
    return storage_image_reference_payload


def convert_present_to_raw_os_disk(os_disk: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        os_disk(Dict(str, Any)) : Specifies information about the operating system disk used by the virtual machine.

    Returns:
        OS Disk Payload Dict[str,any] in the format of an Azure PUT operation payload.
    """
    os_disk_payload = {
        "name": os_disk.get("disk_name"),
        "diskSizeGB": os_disk.get("disk_size_in_GB"),
        "caching": os_disk.get("disk_caching"),
        "createOption": os_disk.get("disk_create_option"),
        "deleteOption": os_disk.get("disk_delete_option"),
        "managedDisk": {
            "id": os_disk.get("disk_id"),
            "storageAccountType": os_disk.get("storage_account_type"),
        },
    }
    return os_disk_payload


def convert_present_to_raw_data_disks(data_disks: List[Dict[str, Any]]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        data_disks(list(Dict[str, Any]) : List of Data Disk payload for VM

    Returns:
        List of Data Disk payload List(Dict[str,any]) in the format of an Azure PUT operation payload.
    """
    data_disks_list: List = []
    for data_disk in data_disks:
        data_disks_payload = {
            "name": data_disk.get("disk_name"),
            "diskSizeGB": data_disk.get("disk_size_in_GB"),
            "lun": data_disk.get("disk_logical_unit_number"),
            "caching": data_disk.get("disk_caching"),
            "createOption": data_disk.get("disk_create_option"),
            "deleteOption": data_disk.get("disk_delete_option"),
            "managedDisk": {
                "id": data_disk.get("disk_id"),
                "storageAccountType": data_disk.get("storage_account_type"),
            },
        }
        data_disks_list.append(data_disks_payload)
    return data_disks_list


def convert_present_to_raw_os_profile(os_profile: Dict[str, Any]):
    """
    Giving some present function inputs, generate a payload that can be used during PUT operation to Azure. Any None
    value input will be ignored, unless this parameter is a required input parameter.

    Args:
        os_profile(Dict[str, Any]) : Operating System profile for VM creation

    Returns:
        OS Profile payload : Dict[str,any] in the format of an Azure PUT operation payload.
    """
    os_profile_payload = {
        "adminUsername": os_profile.get("admin_username"),
        "adminPassword": os_profile.get("admin_password"),
        "computerName": os_profile.get("computer_name"),
    }
    return os_profile_payload


def convert_raw_to_present_os_profile(os_profile: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        os_profile(Dict, optional): OS Profile payload in a virtual machine resource

    Returns:
         OS Profile payload that contains the parameters that match respective present function's input format.
    """
    os_profile_payload = {
        "admin_username": os_profile.get("adminUsername"),
        "computer_name": os_profile.get("computerName"),
    }
    return os_profile_payload


def convert_raw_to_present_network_interface(network_interfaces: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        network_interfaces(list[Dict], optional): Resource List of Network Interfaces in a virtual machine resource.

    Returns:
         A Network Interface Id List that contains the parameters that match respective present function's input format.
    """
    present_network_interfaces: List = []
    for network_interface in network_interfaces:
        present_network_interfaces.append(network_interface.get("id"))
    return present_network_interfaces


def convert_raw_to_present_image_reference(image_reference: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        image_reference(Dict, optional): Image Reference payload in a virtual machine resource.

    Returns:
         Image Reference payload contains the parameters that match respective present function's input format.
    """
    image_reference_payload = {
        "image_sku": image_reference.get("sku"),
        "image_publisher": image_reference.get("publisher"),
        "image_version": image_reference.get("version"),
        "image_offer": image_reference.get("offer"),
    }
    return image_reference_payload


def convert_raw_to_present_os_disk(os_disk: Dict[str, Any]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        os_disk(Dict, optional): OS Disk payload in a virtual machine resource.

    Returns:
         OS Disk payload that contains the parameters that match respective present function's input format.
    """
    os_disk_payload = {
        "disk_name": os_disk.get("name"),
        "disk_caching": os_disk.get("caching"),
    }
    if os_disk.get("diskSizeGB") is not None:
        os_disk_payload["disk_size_in_GB"] = os_disk.get("diskSizeGB")
    if (
        os_disk.get("managedDisk") is not None
        and os_disk.get("managedDisk").get("storageAccountType") is not None
    ):
        os_disk_payload["storage_account_type"] = os_disk.get("managedDisk").get(
            "storageAccountType"
        )
    if (
        os_disk.get("managedDisk") is not None
        and os_disk.get("managedDisk").get("id") is not None
    ):
        os_disk_payload["disk_id"] = os_disk.get("managedDisk").get("id")
    if os_disk.get("createOption") is not None:
        os_disk_payload["disk_create_option"] = os_disk.get("createOption")
    if os_disk.get("deleteOption") is not None:
        os_disk_payload["disk_delete_option"] = os_disk.get("deleteOption")
    return os_disk_payload


def convert_raw_to_present_data_disks(data_disks: List[Dict[str, Any]]):
    """
     Giving an existing resource state and desired state inputs, generate a Dict that match the format of
     present input parameters.

    Args:
        data_disks(list[Dict], optional): Resource List of Data Disks in a virtual machine resource.

    Returns:
         A Data Disk List that contains the parameters that match respective present function's input format.
    """
    present_data_disks_payload: List = []
    for data_disk in data_disks:
        data_disk_payload = {
            "disk_name": data_disk.get("name"),
            "disk_logical_unit_number": data_disk.get("lun"),
            "disk_caching": data_disk.get("caching"),
        }
        if data_disk.get("diskSizeGB") is not None:
            data_disk_payload["disk_size_in_GB"] = data_disk.get("diskSizeGB")
        if (
            data_disk.get("managedDisk") is not None
            and data_disk.get("managedDisk").get("storageAccountType") is not None
        ):
            data_disk_payload["storage_account_type"] = data_disk.get(
                "managedDisk"
            ).get("storageAccountType")
        if (
            data_disk.get("managedDisk") is not None
            and data_disk.get("managedDisk").get("id") is not None
        ):
            data_disk_payload["disk_id"] = data_disk.get("managedDisk").get("id")
        if data_disk.get("createOption") is not None:
            data_disk_payload["disk_create_option"] = data_disk.get("createOption")
        if data_disk.get("deleteOption") is not None:
            data_disk_payload["disk_delete_option"] = data_disk.get("deleteOption")
        present_data_disks_payload.append(data_disk_payload)
    return present_data_disks_payload


def compare_network_interface_payload(
    existing_network_interface_list: List[Dict[str, Any]],
    network_interface_ids: List[str],
):
    """
    Compares network interface payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_network_interface_list(list[Dict]): Existing Network Interface payload
        network_interface_ids(list[str]): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    if len(network_interface_ids) != len(existing_network_interface_list):
        return True
    existing_network_interface_id_list = []
    for existing_network_interface in existing_network_interface_list:
        existing_network_interface_id_list.append(existing_network_interface.get("id"))
    return set(existing_network_interface_id_list) != set(network_interface_ids)


def compare_storage_os_disk_payload(
    existing_storage_os_disk_payload: Dict[str, Any],
    new_storage_os_disk: Dict[str, Any],
):
    """
    Compares OS Disk payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_os_disk_payload[Dict]: Existing Storage OS Disk payload
        new_storage_os_disk[Dict]: Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    os_disk_present_converted_payload = convert_raw_to_present_os_disk(
        existing_storage_os_disk_payload
    )
    return compare_update_dict_payload(
        os_disk_present_converted_payload, new_storage_os_disk
    )


def compare_storage_data_disks_payload(
    existing_storage_data_disks_payload: List[Dict[str, Any]],
    new_storage_data_disks: List[Dict[str, Any]],
):
    """
    Compares Data Disks payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_data_disks_payload(list[Dict]): Existing Storage Data Disk payload
        new_storage_data_disks(list[str]): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    data_disks_present_converted_payload = convert_raw_to_present_data_disks(
        existing_storage_data_disks_payload
    )
    if len(data_disks_present_converted_payload) != len(new_storage_data_disks):
        return True
    existing_payload_map = {}
    for element in data_disks_present_converted_payload:
        existing_payload_map[element.get("disk_name")] = element

    return compare_update_dict_list_payload(
        existing_payload_map, new_storage_data_disks
    )


def compare_storage_image_reference_payload(
    existing_storage_image_reference_payload: Dict[str, Any],
    new_storage_image_reference: Dict[str, Any],
):
    """
    Compares Storage Image Reference payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_storage_image_reference_payload(Dict): Existing Storage Image Reference payload
        new_storage_image_reference(Dict): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    storage_image_reference_present_converted_payload = (
        convert_raw_to_present_image_reference(existing_storage_image_reference_payload)
    )
    return compare_update_dict_payload(
        storage_image_reference_present_converted_payload, new_storage_image_reference
    )


def compare_os_profile_payload(
    existing_os_profile_payload: Dict[str, Any], new_os_profile: Dict[str, Any]
):
    """
    Compares OS Profile payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_os_profile_payload(Dict): Existing OS Profile payload
        new_os_profile(Dict): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    os_profile_present_converted_payload = convert_raw_to_present_os_profile(
        existing_os_profile_payload
    )
    new_os_profile_copy = copy.deepcopy(new_os_profile)
    # azure payload does not contain admin_password
    new_os_profile_copy.pop("admin_password", None)
    return compare_update_dict_payload(
        os_profile_present_converted_payload, new_os_profile_copy
    )


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


def compare_update_dict_list_payload(
    existing_payload_map: Dict[str, Any], update_payload: List[Dict[str, Any]]
):
    """
    Compares the payload to check whether any of the state attributes has been added or modified.
    Returns true if there is any updates else false.

    Args:
        existing_payload_map(Dict): Existing payload Map
        update_payload(List(Dict)): Present value which will be given as input

    Returns:
        A boolean value, True if there is any difference between the arguments else returns False
    """
    for update_element in update_payload:
        disk_name = update_element.get("disk_name")
        if disk_name in existing_payload_map:
            if compare_update_dict_payload(
                existing_payload_map.get(disk_name), update_element
            ):
                return True
        else:
            return True
    return False


def merge_dictionary_payloads(
    existing_payload: Dict[str, Any], update_payload: Dict[str, Any]
):
    """
    Merge the input payload with the payload from Azure Get Response
    Returns the merged payload

    Args:
        existing_payload(Dict): Existing payload From Azure Get API
        update_payload(Dict): Present value which will be given as input

    Returns:
        A Dict of the merged Payload
    """
    existing_payload_copy = copy.deepcopy(existing_payload)
    for update_element_key in update_payload:
        if update_payload.get(update_element_key) is not None:
            existing_payload_copy[update_element_key] = update_payload.get(
                update_element_key
            )
    return existing_payload_copy


def merge_data_disks_payloads(
    existing_payload: List[Dict[str, Any]], update_payload: List[Dict[str, Any]]
):
    """
    Merge the input payload with the payload from Azure Get Response for Data Disks
    Returns the merged Data Disk payload

    Args:
        existing_payload(Dict): Existing payload Map
        update_payload(Dict): Present value which will be given as input

    Returns:
        A Dict of the merged Data Disks Payload
    """
    existing_payload_map = {}
    existing_merged_payload = []
    for element in existing_payload:
        existing_payload_map[element.get("disk_name")] = element
    for update_element in update_payload:
        disk_name = update_element.get("disk_name")
        if disk_name in existing_payload_map:
            # Merge Data
            existing_merged_payload.append(
                merge_dictionary_payloads(
                    existing_payload_map.get(disk_name), update_element
                )
            )
        else:
            # Keep new input data
            existing_merged_payload.append(update_element)
    return existing_merged_payload
