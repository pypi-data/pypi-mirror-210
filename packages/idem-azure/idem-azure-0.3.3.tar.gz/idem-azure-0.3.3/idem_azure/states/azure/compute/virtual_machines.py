"""State module for managing Compute Virtual Machine."""
import copy
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
    resource_group_name: str,
    virtual_machine_name: str,
    location: str,
    virtual_machine_size: str,
    network_interface_ids: List[str],
    os_profile: make_dataclass(
        "OsProfile",
        [
            ("computer_name", str),
            ("admin_username", str),
            ("admin_password", str),
        ],
    ),
    storage_image_reference: make_dataclass(
        "OsProfile",
        [
            ("image_sku", str),
            ("image_publisher", str),
            ("image_version", str),
            ("image_offer", str),
        ],
    ),
    storage_os_disk: make_dataclass(
        "StorageOsDisk",
        [
            ("disk_name", str),
            ("disk_size_in_GB", int),
            ("disk_caching", str),
            ("disk_create_option", str),
            ("disk_delete_option", str),
            ("disk_id", str),
            ("storage_account_type", str),
        ],
    ),
    storage_data_disks: List[
        make_dataclass(
            "StorageDataDisks",
            [
                ("disk_name", str),
                ("disk_size_in_GB", int),
                ("disk_logical_unit_number", int),
                ("disk_caching", str),
                ("disk_create_option", str),
                ("disk_delete_option", str),
                ("disk_id", str),
                ("storage_account_type", str),
            ],
        )
    ] = None,
    resource_id: str = None,
    subscription_id: str = None,
    tags: Dict[str, str] = None,
) -> Dict:
    r"""Create or update Virtual Machines.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        resource_id(str, Optional): Virtual Machine resource id on Azure
        virtual_machine_name(str): The name of the virtual machine.
        location(str): Resource location. Changing this forces a new resource to be created.
        virtual_machine_size(str): Specifies the size of the Virtual Machine.
        network_interface_ids(list[str]): A list of Network Interface IDs which should be associated with the Virtual Machine.
        subscription_id(str, Optional): Subscription Unique id.
        tags(dict[str, str], Optional): Resource tags.
        os_profile(dict[str, Any]): Specifies the operating system settings used while creating the virtual machine.

            * computer_name(str):
                Specifies the name of the Virtual Machine.
            * admin_username(str):
                Specifies the name of the local administrator account.
            * admin_password(str):
                (Required for Windows, Optional for Linux) The password associated with the local administrator account.
        storage_image_reference(dict[str, Any]): Specifies information about the image to use. Eg- platform images, marketplace images.

            * image_sku(str):
                Specifies the SKU of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_publisher(str):
                Specifies the publisher of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_version(str):
                Specifies the version of the image used to create the virtual machine. Changing this forces a new resource to be created.
            * image_offer(str, Optional):
                Specifies the offer of the image used to create the virtual machine. Changing this forces a new resource to be created.
        storage_os_disk(dict[str, Any]): Specifies information about the operating system disk used by the virtual machine.

            * disk_name(str):
                Specifies the name of the OS Disk.
            * disk_create_option(str):
                Specifies how the OS Disk should be created. Possible values are Attach (managed disks only) and FromImage.
            * storage_account_type(str, Optional):
                Specifies the type of Managed Disk which should be created. Possible values are Standard_LRS, StandardSSD_LRS or Premium_LRS.
            * disk_caching(str, Optional):
                Specifies the caching requirements for the OS Disk. Possible values include None, ReadOnly and ReadWrite.
            * disk_size_in_GB(str, Optional):
                Specifies the size of the OS Disk in gigabytes.
            * disk_delete_option(str, Optional):
                Specifies how the OS Disk should be handled after VM deletion. Possible values are Detach and Delete.
            * disk_id(str, Optional):
                Specifies the ID of an existing Managed Disk which should be attached as the OS Disk of this Virtual Machine. If this is set then the create_option must be set to Attach.
        storage_data_disks(list(dict[str, Any]), Optional): List of Data disks attached/added to a VM.

            * disk_name(str):
                The name of the Data Disk.
            * disk_create_option(str):
                Specifies how the data disk should be created. Possible values are Attach, FromImage and Empty.
            * disk_logical_unit_number(str):
                Specifies the logical unit number of the data disk. This needs to be unique within all the Data Disks on the Virtual Machine.
            * storage_account_type(str, Optional):
                Specifies the type of managed disk to create. Possible values are either Standard_LRS, StandardSSD_LRS, Premium_LRS or UltraSSD_LRS.
            * disk_caching(str, Optional):
                Specifies the caching requirements for the Data Disk. Possible values include None, ReadOnly and ReadWrite.
            * disk_size_in_GB(str, Optional):
                Specifies the size of the data disk in gigabytes.
            * disk_delete_option(str, Optional):
                Specifies how the OS Disk should be handled after VM deletion. Possible values are Detach and Delete.
            * disk_id(str, Optional):
                Specifies the ID of an Existing Managed Disk which should be attached to this Virtual Machine. When this field is set create_option must be set to Attach.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_present:
              azure.compute.virtual_machines.present:
                - name: my-vm
                - resource_group_name: my-rg-1
                - virtual_machine_name: my-vm
                - location: eastus
                - virtual_machine_size: Standard_B1ls
                - network_interface_ids:
                  - /subscriptions/subscription_id/resourceGroups/my-rg-1/providers/Microsoft.Network/networkInterfaces/my-nic-id-1
                - storage_image_reference:
                    image_sku: 18.04-LTS
                    image_publisher: Canonical
                    image_version: latest
                    image_offer: UbuntuServer
                - storage_os_disk:
                    storage_account_type: Standard_LRS
                    disk_name: my-os-disk
                    disk_caching: ReadWrite
                    disk_size_in_GB: 30
                    disk_create_option: FromImage
                    disk_delete_option: Detach
                - storage_data_disks:
                  - disk_name: my-data-disk
                    disk_size_in_GB: 2
                    disk_logical_unit_number: 0
                    disk_caching: None
                    disk_create_option: Empty
                    disk_delete_option: Delete
                - os_profile:
                    admin_username: my-admin-username
                    computer_name: machine-name
                    admin_password: Vmwareadmin123!
                - tags:
                    my-tag-key-1: my-tag-value-1
                    my-tag-key-2: my-tag-value-2
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
        resource_id = (
            f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
            f"/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"
        )
    response_get = await hub.exec.azure.compute.virtual_machines.get(
        ctx, resource_id=resource_id, raw=True
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.compute.virtual_machines {response_get['comment']} {response_get['ret']}"
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
                    "virtual_machine_name": virtual_machine_name,
                    "virtual_machine_size": virtual_machine_size,
                    "tags": tags,
                    "location": location,
                    "network_interface_ids": network_interface_ids,
                    "storage_image_reference": storage_image_reference,
                    "storage_os_disk": storage_os_disk,
                    "storage_data_disks": storage_data_disks,
                    "os_profile": os_profile,
                    "resource_id": resource_id,
                },
            )
            result["comment"].append(
                f"Would create azure.compute.virtual_machines '{name}'"
            )
            return result

        else:
            # PUT operation to create a resource
            payload = hub.tool.azure.compute.virtual_machines.convert_present_to_raw_virtual_machine(
                location=location,
                virtual_machine_size=virtual_machine_size,
                network_interface_ids=network_interface_ids,
                storage_image_reference=storage_image_reference,
                storage_os_disk=storage_os_disk,
                storage_data_disks=storage_data_disks,
                os_profile=os_profile,
                tags=tags,
            )

            response_put = await hub.exec.request.json.put(
                ctx,
                url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-03-01",
                success_codes=[200, 201],
                json=payload,
            )
            if not response_put["result"]:
                hub.log.debug(
                    f"Could not create azure.compute.virtual_machines {response_put['comment']} {response_put['ret']}"
                )
                result["comment"] = [response_put["comment"], response_put["ret"]]
                result["result"] = False
                return result

            result[
                "new_state"
            ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                resource=response_put["ret"],
                idem_resource_name=name,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                virtual_machine_name=virtual_machine_name,
                resource_id=resource_id,
            )
            result["comment"].append(f"Created azure.compute.virtual_machines '{name}'")
            return result
    else:
        existing_resource = response_get["ret"]
        result[
            "old_state"
        ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
            resource=existing_resource,
            idem_resource_name=name,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            virtual_machine_name=virtual_machine_name,
            resource_id=resource_id,
        )
        # Generate a new PUT operation payload with new values
        new_payload = (
            hub.tool.azure.compute.virtual_machines.update_virtual_machine_payload(
                response_get["ret"],
                {
                    "virtual_machine_size": virtual_machine_size,
                    "storage_data_disks": storage_data_disks,
                    "network_interface_ids": network_interface_ids,
                    "storage_os_disk": storage_os_disk,
                    "os_profile": os_profile,
                    "storage_image_reference": storage_image_reference,
                    "tags": tags,
                },
            )
        )
        if ctx.get("test", False):
            if new_payload["ret"] is None:
                result["new_state"] = copy.deepcopy(result["old_state"])
                result["comment"].append(
                    f"azure.compute.virtual_machines '{name}' has no property need to be updated."
                )
            else:
                result[
                    "new_state"
                ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
                    resource=new_payload["ret"],
                    idem_resource_name=name,
                    subscription_id=subscription_id,
                    resource_group_name=resource_group_name,
                    virtual_machine_name=virtual_machine_name,
                    resource_id=resource_id,
                )
                result["comment"].append(
                    f"Would update azure.compute.virtual_machines '{name}'"
                )
            return result
        # PUT operation to update a resource
        if new_payload["ret"] is None:
            result["new_state"] = copy.deepcopy(result["old_state"])
            result["comment"].append(
                f"azure.compute.virtual_machines '{name}' has no property need to be updated."
            )
            return result
        result["comment"] += new_payload["comment"]

        response_put = await hub.exec.request.json.put(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-03-01",
            success_codes=[200, 201],
            json=new_payload["ret"],
        )
        if not response_put["result"]:
            hub.log.debug(
                f"Could not update azure.compute.virtual_machines {response_put['comment']} {response_put['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_put["comment"], response_put["ret"]]
            return result

        result[
            "new_state"
        ] = hub.tool.azure.compute.virtual_machines.convert_raw_virtual_machine_to_present(
            resource=response_put["ret"],
            idem_resource_name=name,
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            virtual_machine_name=virtual_machine_name,
            resource_id=resource_id,
        )
        if result["old_state"] == result["new_state"]:
            result["comment"].append(
                f"azure.compute.virtual_machines '{name}' has no property need to be updated."
            )
            return result

        result["comment"].append(f"Updated azure.compute.virtual_machines '{name}'")
        return result


async def absent(
    hub,
    ctx,
    name: str,
    resource_group_name: str,
    virtual_machine_name: str,
    subscription_id: str = None,
) -> Dict:
    r"""Delete a Virtual Machine.

    Args:
        name(str): The identifier for this state.
        resource_group_name(str): The name of the resource group.
        virtual_machine_name(str): The name of the virtual machine.
        subscription_id(str, Optional): Subscription Unique id.

    Returns:
        Dict

    Examples:
        .. code-block:: sls

            resource_is_absent:
              azure.compute.virtual_machines.absent:
                - name: my-vm
                - resource_group_name: my-resource-group
                - virtual_machine_name: my-vm
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
    resource_id = (
        f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
        f"/providers/Microsoft.Compute/virtualMachines/{virtual_machine_name}"
    )
    response_get = await hub.exec.azure.compute.virtual_machines.get(
        ctx,
        resource_id=resource_id,
    )
    if not response_get["result"]:
        hub.log.debug(
            f"Could not get azure.compute.virtual_machines '{name}' {response_get['comment']} {response_get['ret']}"
        )
        result["result"] = False
        result["comment"] = [response_get["comment"], response_get["ret"]]
        return result

    if response_get["ret"]:
        result["old_state"] = response_get["ret"]
        result["old_state"]["name"] = name

        if ctx.get("test", False):
            result["comment"].append(
                f"Would delete azure.compute.virtual_machines '{name}'"
            )
            return result

        response_delete = await hub.exec.request.raw.delete(
            ctx,
            url=f"{ctx.acct.endpoint_url}{resource_id}?api-version=2022-03-01",
            success_codes=[200, 202, 204],
        )

        if not response_delete["result"]:
            hub.log.debug(
                f"Could not delete azure.compute.virtual_machines {response_delete['comment']} {response_delete['ret']}"
            )
            result["result"] = False
            result["comment"] = [response_delete["comment"], response_delete["ret"]]
            return result

        result["comment"].append(f"Deleted azure.compute.virtual_machines '{name}'")
        return result

    else:
        # If Azure returns 'Not Found' error, it means the resource has been absent.
        result["comment"].append(
            f"azure.compute.virtual_machines '{name}' already absent"
        )
        return result


async def describe(hub, ctx) -> Dict[str, Dict[str, Any]]:
    r"""Describe the resource in a way that can be recreated/managed with the corresponding "present" function.

    Lists all Virtual Machines under the same subscription.


    Returns:
        Dict[str, Any]

    Examples:
        .. code-block:: bash

            $ idem describe azure.compute.virtual_machines
    """
    result = {}
    ret_list = await hub.exec.azure.compute.virtual_machines.list(ctx)
    if not ret_list["ret"]:
        hub.log.debug(
            f"Could not describe compute virtual_machines {ret_list['comment']}"
        )
        return result

    for resource in ret_list["ret"]:
        resource_id = resource["resource_id"]
        result[resource_id] = {
            "azure.compute.virtual_machines.present": [
                {parameter_key: parameter_value}
                for parameter_key, parameter_value in resource.items()
            ]
        }
    return result
