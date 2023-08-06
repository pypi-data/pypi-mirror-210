import requests
import json
import django.utils.text

from colorama import Fore, Style, init
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
from datetime import datetime
from requests import api
from dcim.models import Manufacturer
from dcim.models import Device, DeviceType
from netbox_cisco_support_plugin.models import CiscoDeviceTypeSupport, CiscoSupport

init(autoreset=True, strip=False)


class Command(BaseCommand):
    help = "Sync local devices with Cisco EoX Support API"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--manufacturer",
            action="store_true",
            default="Cisco",
            help="Manufacturer name (default: Cisco)",
        )

    def task_title(self, title: str) -> None:
        """
        Prints a Nornir style title.
        """
        msg = f"**** {title} "
        return f"\n{Style.BRIGHT}{Fore.GREEN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    def task_name(self, text: str) -> None:
        """
        Prints a Nornir style host task title.
        """
        msg = f"{text} "
        return f"\n{Style.BRIGHT}{Fore.CYAN}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    def task_info(self, text: str, changed: bool) -> str:
        """
        Returns a Nornir style task info message.
        """
        color = Fore.YELLOW if changed else Fore.GREEN
        msg = f"---- {text} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{color}{msg}{'-' * (90 - len(msg))} INFO{Fore.RESET}{Style.RESET_ALL}"


    def task_error(self, text: str, changed: bool) -> str:
        """
        Returns a Nornir style task error message.
        """
        msg = f"---- {text} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{Fore.RED}{msg}{'-' * (90 - len(msg))} ERROR{Fore.RESET}{Style.RESET_ALL}"


    def task_host(self, host: str, changed: bool) -> str:
        """
        Returns a Nornir style host task name.
        """
        msg = f"* {host} ** changed : {str(changed)} "
        return f"{Style.BRIGHT}{Fore.BLUE}{msg}{'*' * (90 - len(msg))}{Fore.RESET}{Style.RESET_ALL}"

    # Updates a single device with current SNI coverage status data
    def update_device_sni_status_data(self, device):
        self.stdout.write(self.style.SUCCESS("Trying to update device %s" % device["sr_no"]))

        # Get the device object from NetBox
        try:
            d = Device.objects.get(serial=device["sr_no"])
        except MultipleObjectsReturned:
            # Error if netbox has multiple SN's and skip updating
            self.stdout.write(
                self.style.NOTICE(
                    "ERROR: Multiple objects exist within Netbox with Serial Number " + device["sr_no"]
                )
            )
            return

        # Check if a CiscoSupport object already exists, if not, create a new one
        try:
            ds = CiscoSupport.objects.get(device=d)
        except CiscoSupport.DoesNotExist:
            ds = CiscoSupport(device=d)

        # A "YES" string is not quite boolean :-)
        covered = True if device["sr_no_owner"] == "YES" else False

        if covered:
            api_status = "API user is associated with contract and device"
        else:
            api_status = "API user is not associated with contract and device (No authorization to most of the API information)"

        self.stdout.write(self.style.SUCCESS("%s - sr_no_owner: %s" % (device["sr_no"], covered)))

        # Update sr_no_owner and api_status
        ds.sr_no_owner = covered
        ds.api_status = api_status

        # Save the CiscoSupport object
        ds.save()

        return

    # Updates a single device with current SNI coverage summary data
    def update_device_sni_summary_data(self, device):
        self.stdout.write(self.style.SUCCESS("Trying to update device %s" % device["sr_no"]))

        # Get the device object from NetBox
        try:
            d = Device.objects.get(serial=device["sr_no"])
        except MultipleObjectsReturned:
            # Error if netbox has multiple SN's and skip updating
            self.stdout.write(
                self.style.NOTICE(
                    "ERROR: Multiple objects exist within Netbox with Serial Number " + device["sr_no"]
                )
            )
            return

        # Check if a CiscoSupport object already exists, if not, create a new one
        try:
            ds = CiscoSupport.objects.get(device=d)
        except CiscoSupport.DoesNotExist:
            ds = CiscoSupport(device=d)

        # A "YES" string is not quite boolean :-)
        covered = True if device["is_covered"] == "YES" else False

        if covered:
            coverage_status = "Covered by Cisco SNTC"
        else:
            coverage_status = "Not covered by Cisco SNTC"

        self.stdout.write(self.style.SUCCESS("%s - covered: %s" % (device["sr_no"], covered)))

        # Update is_covered and coverage_status
        ds.is_covered = covered
        ds.coverage_status = coverage_status

        try:
            if not device["service_contract_number"]:
                self.stdout.write(self.style.NOTICE("%s has no service_contract_number" % device["sr_no"]))
            else:
                service_contract_number = device["service_contract_number"]
                self.stdout.write(
                    self.style.SUCCESS(
                        "%s - service_contract_number: %s" % (device["sr_no"], service_contract_number)
                    )
                )

                # Update service_contract_number
                ds.service_contract_number = service_contract_number

        except KeyError:
            self.stdout.write(self.style.NOTICE("%s has no service_contract_number" % device["sr_no"]))

        try:
            if not device["service_line_descr"]:
                self.stdout.write(self.style.NOTICE("%s has no service_line_descr" % device["sr_no"]))
            else:
                service_line_descr = device["service_line_descr"]
                self.stdout.write(
                    self.style.SUCCESS("%s - service_line_descr: %s" % (device["sr_no"], service_line_descr))
                )

                # Update service_line_descr
                ds.service_line_descr = service_line_descr

        except KeyError:
            self.stdout.write(self.style.NOTICE("%s has no service_line_descr" % device["sr_no"]))

        try:
            if not device["warranty_type"]:
                self.stdout.write(self.style.NOTICE("%s has no warranty_type" % device["sr_no"]))
            else:
                warranty_type_string = device["warranty_type"]
                warranty_type = datetime.strptime(warranty_type_string, "%Y-%m-%d").date()
                self.stdout.write(
                    self.style.SUCCESS("%s - warranty_type: %s" % (device["sr_no"], warranty_type))
                )

                # Update warranty_type
                ds.warranty_type = warranty_type

        except KeyError:
            self.stdout.write(self.style.NOTICE("%s has no warranty_type" % device["sr_no"]))

        try:
            if not device["warranty_end_date"]:
                self.stdout.write(self.style.NOTICE("%s has no warranty_end_date" % device["sr_no"]))
            else:
                warranty_end_date = device["warranty_end_date"]
                self.stdout.write(
                    self.style.SUCCESS("%s - warranty_end_date: %s" % (device["sr_no"], warranty_end_date))
                )

                # Update warranty_end_date
                ds.warranty_end_date = warranty_end_date

        except KeyError:
            self.stdout.write(self.style.NOTICE("%s has no warranty_end_date" % device["sr_no"]))

        try:
            if not device["covered_product_line_end_date"]:
                self.stdout.write(
                    self.style.NOTICE("%s has no covered_product_line_end_date" % device["sr_no"])
                )
            else:
                coverage_end_date_string = device["covered_product_line_end_date"]
                coverage_end_date = datetime.strptime(coverage_end_date_string, "%Y-%m-%d").date()
                self.stdout.write(
                    self.style.SUCCESS("%s - coverage_end_date: %s" % (device["sr_no"], coverage_end_date))
                )

                # Update coverage_end_date
                ds.coverage_end_date = coverage_end_date

        except KeyError:
            self.stdout.write(self.style.NOTICE("%s has no coverage_end_date" % device["sr_no"]))

        # Save the CiscoSupport object
        ds.save()

        return

    def update_device_type_eox_data(self, pid, eox_data):
        try:
            # Get the device type object for the supplied PID
            dt = DeviceType.objects.get(part_number=pid)

        except MultipleObjectsReturned:
            # Error if netbox has multiple PN's
            self.stdout.write(
                self.style.NOTICE("ERROR: Multiple objects exist within Netbox with Part Number " + pid)
            )
            return

        # Check if CiscoDeviceTypeSupport record already exists
        try:
            dts = CiscoDeviceTypeSupport.objects.get(device_type=dt)
        # If not, create a new one for this Device Type
        except CiscoDeviceTypeSupport.DoesNotExist:
            dts = CiscoDeviceTypeSupport(device_type=dt)

        try:
            # Check if JSON contains EOXError with value field starting with Incorrect PID
            # Incorrect PID happen when no EOX information exists for that PID
            if "Incorrect PID:" in eox_data["EOXRecord"][0]["EOXError"]["ErrorDescription"]:
                eox_error = f"EoX Support Information Not Announced"
                self.stdout.write(self.style.SUCCESS("%s - EoX Support Information Not Announced" % pid))
            else:
                eox_error = eox_data["EOXRecord"][0]["EOXError"]["ErrorDescription"]
                self.stdout.write(self.style.NOTICE("%s - EoXError: %s" % (pid, eox_error)))

            # Update eox_error
            dts.eox_error = eox_error

        # Do nothing when JSON field does not exist
        except KeyError:
            self.stdout.write(self.style.NOTICE("%s  - EOX Support Information Announced" % pid))

        try:
            # Check if JSON contains EOXExternalAnnouncementDate with value field
            if not eox_data["EOXRecord"][0]["EOXExternalAnnouncementDate"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no eox_announcement_date" % pid))
            else:
                eox_announcement_date_string = eox_data["EOXRecord"][0]["EOXExternalAnnouncementDate"][
                    "value"
                ]
                # Cast this value to datetime.date object
                eox_announcement_date = datetime.strptime(eox_announcement_date_string, "%Y-%m-%d").date()
                self.stdout.write(
                    self.style.NOTICE("%s - eox_announcement_date: %s" % (pid, eox_announcement_date))
                )

                # Update eox_announcement_date
                dts.eox_announcement_date = eox_announcement_date

        # Do nothing when JSON field does not exist
        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no eox_announcement_date" % pid))

        try:
            # Check if JSON contains EndOfSaleDate with value field
            if not eox_data["EOXRecord"][0]["EndOfSaleDate"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_sale_date" % pid))
            else:
                end_of_sale_date_string = eox_data["EOXRecord"][0]["EndOfSaleDate"]["value"]
                # Cast this value to datetime.date object
                end_of_sale_date = datetime.strptime(end_of_sale_date_string, "%Y-%m-%d").date()
                self.stdout.write(self.style.NOTICE("%s - end_of_sale_date: %s" % (pid, end_of_sale_date)))

                # Update end_of_sale_date
                dts.end_of_sale_date = end_of_sale_date

        # Do nothing when JSON field does not exist
        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_sale_date" % pid))

        try:
            if not eox_data["EOXRecord"][0]["EndOfSWMaintenanceReleases"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_sw_maintenance_releases" % pid))
            else:
                end_of_sw_maintenance_releases_string = eox_data["EOXRecord"][0][
                    "EndOfSWMaintenanceReleases"
                ]["value"]
                end_of_sw_maintenance_releases = datetime.strptime(
                    end_of_sw_maintenance_releases_string, "%Y-%m-%d"
                ).date()
                self.stdout.write(
                    self.style.NOTICE(
                        "%s - end_of_sw_maintenance_releases: %s" % (pid, end_of_sw_maintenance_releases)
                    )
                )

                # Update end_of_sw_maintenance_releases
                dts.end_of_sw_maintenance_releases = end_of_sw_maintenance_releases

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_sw_maintenance_releases" % pid))

        try:
            if not eox_data["EOXRecord"][0]["EndOfSecurityVulSupportDate"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_security_vul_support_date" % pid))
            else:
                end_of_security_vul_support_date_string = eox_data["EOXRecord"][0][
                    "EndOfSecurityVulSupportDate"
                ]["value"]
                end_of_security_vul_support_date = datetime.strptime(
                    end_of_security_vul_support_date_string, "%Y-%m-%d"
                ).date()
                self.stdout.write(
                    self.style.NOTICE(
                        "%s - end_of_security_vul_support_date: %s" % (pid, end_of_security_vul_support_date)
                    )
                )

                # Update
                dts.end_of_security_vul_support_date = end_of_security_vul_support_date

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_security_vul_support_date" % pid))

        try:
            if not eox_data["EOXRecord"][0]["EndOfRoutineFailureAnalysisDate"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_routine_failure_analysis_date" % pid))
            else:
                end_of_routine_failure_analysis_date_string = eox_data["EOXRecord"][0][
                    "EndOfRoutineFailureAnalysisDate"
                ]["value"]
                end_of_routine_failure_analysis_date = datetime.strptime(
                    end_of_routine_failure_analysis_date_string, "%Y-%m-%d"
                ).date()
                self.stdout.write(
                    self.style.NOTICE(
                        "%s - end_of_routine_failure_analysis_date: %s"
                        % (pid, end_of_routine_failure_analysis_date)
                    )
                )

                # Update end_of_routine_failure_analysis_date
                dts.end_of_routine_failure_analysis_date = end_of_routine_failure_analysis_date

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_routine_failure_analysis_date" % pid))

        try:
            if not eox_data["EOXRecord"][0]["EndOfServiceContractRenewal"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_service_contract_renewal" % pid))
            else:
                end_of_service_contract_renewal_string = eox_data["EOXRecord"][0][
                    "EndOfServiceContractRenewal"
                ]["value"]
                end_of_service_contract_renewal = datetime.strptime(
                    end_of_service_contract_renewal_string, "%Y-%m-%d"
                ).date()
                self.stdout.write(
                    self.style.NOTICE(
                        "%s - end_of_service_contract_renewal: %s" % (pid, end_of_service_contract_renewal)
                    )
                )

                # Update end_of_service_contract_renewal
                dts.end_of_service_contract_renewal = end_of_service_contract_renewal

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_service_contract_renewal" % pid))

        try:
            if not eox_data["EOXRecord"][0]["LastDateOfSupport"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no last_date_of_support" % pid))
            else:
                last_date_of_support_string = eox_data["EOXRecord"][0]["LastDateOfSupport"]["value"]
                last_date_of_support = datetime.strptime(last_date_of_support_string, "%Y-%m-%d").date()
                self.stdout.write(
                    self.style.NOTICE("%s - last_date_of_support: %s" % (pid, last_date_of_support))
                )

                # Update last_date_of_support
                dts.last_date_of_support = last_date_of_support

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no last_date_of_support" % pid))

        try:
            if not eox_data["EOXRecord"][0]["EndOfSvcAttachDate"]["value"]:
                self.stdout.write(self.style.SUCCESS("%s has no end_of_svc_attach_date" % pid))
            else:
                end_of_svc_attach_date_string = eox_data["EOXRecord"][0]["EndOfSvcAttachDate"]["value"]
                end_of_svc_attach_date = datetime.strptime(end_of_svc_attach_date_string, "%Y-%m-%d").date()
                self.stdout.write(
                    self.style.NOTICE("%s - end_of_svc_attach_date: %s" % (pid, end_of_svc_attach_date))
                )

                # Update end_of_svc_attach_date
                dts.end_of_svc_attach_date = end_of_svc_attach_date

        except KeyError:
            self.stdout.write(self.style.SUCCESS("%s has no end_of_svc_attach_date" % pid))

        # Save the CiscoDeviceTypeSupport object
        dts.save()

        return

    def get_device_types(self, manufacturer):
        task="Get manufacturer"
        self.stdout.write(self.task_name(text=task))

        # trying to get the right manufacturer for this plugin
        try:
            m = Manufacturer.objects.get(name=manufacturer)
        except Manufacturer.DoesNotExist:
            self.stdout.write(self.task_error(text=task, changed=False))
            self.stdout.write(f"Manufacturer {manufacturer} does not exist")

        self.stdout.write(self.task_info(text=task, changed=False))
        self.stdout.write(f"Found manufacturer {m}")

        # trying to get all device types and it's base PIDs associated with this manufacturer
        try:
            dt = DeviceType.objects.filter(manufacturer=m)
        except DeviceType.DoesNotExist:
            self.stdout.write(self.task_error(text=task, changed=False))
            self.stdout.write(f"Manufacturer {m} has no Device Types")

        return dt

    def get_product_ids(self, manufacturer):
        product_ids = []

        # Get all device types for supplied manufacturer
        dt = self.get_device_types(manufacturer)

        task="Get all device types"
        self.stdout.write(self.task_name(text=task))

        # Iterate all this device types
        for device_type in dt:
            # Skip if the device type has no valid part number. Part numbers must match the exact Cisco Base PID
            if not device_type.part_number:
                self.stdout.write(self.task_error(text=task, changed=False))
                self.stdout.write(f"Found device type {device_type} WITHOUT part number - SKIPPING")
                continue

            # Found Part number, append it to the list (PID collection for EoX data done)
            self.stdout.write(self.task_info(text=task, changed=False))
            self.stdout.write(f"Found device type {device_type} with Part Number {device_type.part_number}")

            product_ids.append(device_type.part_number)

        return product_ids

    def get_serial_numbers(self, manufacturer):
        serial_numbers = []

        # Get all device types for supplied manufacturer
        dt = self.get_device_types(manufacturer)

        task="Get all devices"
        self.stdout.write(self.task_name(text=task))

        # Iterate all this device types
        for device_type in dt:
            # trying to get all devices and its serial numbers for this device type (for contract data)
            try:
                d = Device.objects.filter(device_type=device_type)

                for device in d:
                    # Skip if the device has no valid serial number.
                    if not device.serial:
                        self.stdout.write(self.task_error(text=task, changed=False))
                        self.stdout.write(f"Found device {device} WITHOUT Serial Number - SKIPPING")
                        continue

                    self.stdout.write(self.task_info(text=task, changed=False))
                    self.stdout.write(f"Found device {device} with Serial Number {device.serial}")

                    serial_numbers.append(device.serial)
            except Device.DoesNotExist:
                self.stdout.write(self.task_error(text=task, changed=False))
                self.stdout.write(f"Device with device type {dt} does not exist")

        return serial_numbers

    def logon(self):
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_cisco_support_plugin", dict())
        CISCO_CLIENT_ID = PLUGIN_SETTINGS.get("cisco_client_id", "")
        CISCO_CLIENT_SECRET = PLUGIN_SETTINGS.get("cisco_client_secret", "")
        # Set the requests timeout for connect and read separatly
        REQUESTS_TIMEOUT = (3.05, 27)

        token_url = "https://id.cisco.com/oauth2/default/v1/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": CISCO_CLIENT_ID,
            "client_secret": CISCO_CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        access_token_response = requests.post(
            url=token_url, params=params, headers=headers, verify=False, timeout=REQUESTS_TIMEOUT
        )

        token = access_token_response.json()["access_token"]

        api_call_headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}

        return api_call_headers

    # Main entry point for the sync_eox_data command of manage.py
    def handle(self, *args, **kwargs):
        PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("netbox_cisco_support_plugin", dict())
        MANUFACTURER = PLUGIN_SETTINGS.get("manufacturer", "Cisco")

        # Logon one time and gather the required API key
        api_call_headers = self.logon()

        # Step 1: Get all PIDs for all Device Types of that particular manufacturer
        self.stdout.write(self.task_title(title="Update Device Type Support Information"))

        product_ids = self.get_product_ids(MANUFACTURER)

        task="Gathering data for all PIDs"
        self.stdout.write(self.task_name(text=task))

        i = 1
        for pid in product_ids:
            url = (
                f"https://apix.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/{pid}?responseencoding=json"
            )
            api_call_response = requests.get(url=url, headers=api_call_headers, verify=False)
            self.stdout.write(self.style.SUCCESS("Call " + url))

            # Validate response from Cisco
            if api_call_response.status_code == 200:
                # Deserialize JSON API Response into Python object "data"
                data = json.loads(api_call_response.text)

                # Call our Device Type Update method for that particular PID
                self.update_device_type_eox_data(pid, data)

                i += 1

            else:
                # Show an error
                self.stdout.write(self.style.ERROR("API Error: " + api_call_response.text))

        # Step 2: Get all Serial Numbers for all Devices of that particular manufacturer
        self.stdout.write(self.task_title(title="Update Device Support Information"))

        serial_numbers = self.get_serial_numbers(MANUFACTURER)

        task="Gathering data for these serial numbers"
        self.stdout.write(self.task_name(text=task))

        i = 1
        while serial_numbers:
            # Pop the first items_to_fetch items of serial_numbers into current_slice and then delete them from serial
            # numbers. We want to pass x items to the API each time we call it
            items_to_fetch = 10
            current_slice = serial_numbers[:items_to_fetch]
            serial_numbers[:items_to_fetch] = []

            # Call the coverage status
            url = "https://apix.cisco.com/sn2info/v2/coverage/owner_status/serial_numbers/%s" % ",".join(
                current_slice
            )
            api_call_response = requests.get(url=url, headers=api_call_headers, verify=False)
            self.stdout.write(self.style.SUCCESS("Call " + url))
            # Validate response from Cisco
            if api_call_response.status_code == 200:
                # Deserialize JSON API Response into Python object "data"
                data = json.loads(api_call_response.text)
                # Iterate through all serial numbers included in the API response
                for device in data["serial_numbers"]:
                    # Call our Device Update method for that particular Device
                    self.update_device_sni_status_data(device)
                i += 1
            else:
                # Show an error
                self.stdout.write(self.style.ERROR("API Error: " + api_call_response.text))

            # Call the coverage summary
            url = "https://apix.cisco.com/sn2info/v2/coverage/summary/serial_numbers/%s" % ",".join(
                current_slice
            )
            api_call_response = requests.get(url=url, headers=api_call_headers, verify=False)
            self.stdout.write(self.style.SUCCESS("Call " + url))
            # Validate response from Cisco
            if api_call_response.status_code == 200:
                # Deserialize JSON API Response into Python object "data"
                data = json.loads(api_call_response.text)
                # Iterate through all serial numbers included in the API response
                for device in data["serial_numbers"]:
                    # Call our Device Update method for that particular Device
                    self.update_device_sni_summary_data(device)
                i += 1
            else:
                # Show an error
                self.stdout.write(self.style.ERROR("API Error: " + api_call_response.text))
