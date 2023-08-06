# External Imports
from wiliot_deployment_tools.api.extended_api import BridgeThroughGatewayAction, ExtendedEdgeClient, GatewayAction, GatewayType
import sys
import time
from time import sleep
import tabulate

# Internal Imports
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.common.utils import mstimestamp_to_timezone
from wiliot_deployment_tools.common.utils_defines import SEP
from wiliot_api.api_client import WiliotCloudError


class FirmwareUpdate(ExtendedEdgeClient):
    def get_gateway_versions(self, gateway_type, include_beta=False):
        """
        Get a list of currently available gateway firmware versions
        :param gateway_type: GatewayType
        :param include_beta: Boolean - Whether to include beta firmware versions
        :return: A list of dictionaries for all available firmware versions
        """
        path = "gateway/version/{}".format(gateway_type.value)
        res = self._get(path, override_client_path='', params={'include_beta': include_beta})
        return res["data"]

    def ota_update(self, args=None, api_key=None, gw=None, owner=None, server=None, ignore_bridges=None, battery_bridges=None):
        """
        doing the ota upgrade from start to finish, will leave the bridges at the same configuration that they were at the
        beginning of the process
        :type args: parser.parse_args()
        :param args: args from command line
        :type api_key: string
        :param api_key: Asset Management api_key (generated in management portal) to connect to wiliot cloud api's
        :type gw: string
        :param gw: gw to config
        :type owner: string
        :param owner: the owner that the gw is of
        :type server: string
        :param server: environment the gw is at (prod / dev / test)
        :type ignore_bridges: list or dictionary
        :param ignore_bridges: iterable object of bridges to update
        :type battery_bridges: list
        :param battery_bridges: bridges that run by battery
                                (will not configure those to ep36 so it will not turn off)
        """
        api_key = args.api_key if args is not None else api_key
        env = server if server is not None else args.server if args is not None and args.server != "prod" else ""
        gws = [args.gw] if args is not None else [gw] if type(gw) is str else gw
        owner = args.owner if args is not None else owner
        ignore_bridges = args.ignore_bridges if args is not None else ignore_bridges if ignore_bridges is not None else []

        brg_list_connected = []
        if len(gws) > 1:
            debug_print("ota_update does not support multiple gws at the moment")
            sys.exit(0)
        for i in range(len(gws)):
            debug_print("gws[i] = " + str(gws[i]))
            brg_list_connected += self.get_connected_brgs(gws[i], ignore_bridges=ignore_bridges)
            debug_print("{} bridges connected to {}".format(len(brg_list_connected), gws[i]))

        debug_print('Connected bridges are: ' + str([b["id"] for b in brg_list_connected]))
        brg_id_list_connected = [b["id"] for b in brg_list_connected]
        if len(brg_id_list_connected) == 0:
            debug_print("No bridge was found, will exit from ota_update()")
            return
        original_config = {}
        for brg in brg_id_list_connected:
            original_config[brg] = self.get_bridge(brg)["config"]
        self.change_brg_config(brg_id_list_connected, {"otaUpgradeEnabled": 0}, ignore_bridges=ignore_bridges)
        self.change_to_brownout(brg_id_list_connected)

        debug_print("Waiting 10 sec to verify OTA disabled and new EP changed in all the bridges")
        time.sleep(10)

        self.print_brgs_versions(brg_list_connected)

        self.run_ota_process(brg_id_list_connected, gws)

        # Reverting the config to the original
        debug_print("Reverting the bridges configuration to the original")
        for brg in brg_id_list_connected:
            debug_print("{}: {}".format(brg, original_config[brg]))
            self.update_bridge_configuration(brg, original_config[brg])

        brg_list_connected_after_ota = []
        if len(gws) > 1:
            debug_print("ota_update does not support multiple gws at the moment")
            sys.exit(0)
        for i in range(len(gws)):
            debug_print("gws[i] = " + str(gws[i]))
            brg_list_connected_after_ota += self.get_connected_brgs(gws[i], ignore_bridges)
            debug_print("{} bridges connected to {}".format(len(brg_list_connected_after_ota), gws[i]))

        self.print_brgs_versions(brg_list_connected_after_ota)
        debug_print("\nDone!")

    def firmware_update(self, gws_list=None, brgs_to_update=None, update_all_connected_bridges=True,
                        desired_version=None,
                        update_to_latest=True, include_beta=False, ignore_bridges=None, action=False, force_update=False):
        """
        function updates GWs and their connected BRGs (OTA) to desired version / latest available version
        :type gws_list: every iterable type
        :param gws_list: list of gateways to update
        :type brgs_to_update: every iterable type
        :param brgs_to_update: list of connected bridge IDs
        :type update_all_connected_bridges: bool
        :param update_all_connected_bridges: if True, update all bridges connected to specified gateways
        :type desired_version: str
        :param desired_version: desired firmware version
        :type update_to_latest: bool
        :param update_to_latest: if True, automatically updates all GWs to latest available version
        :type include_beta: bool
        :param include_beta: if True, will update to latest available beta firmware
        :type ignore_bridges: list
        :param ignore_bridges: bridges to ignore
        :type action: bool
        :param action: if True, do OTA using GW Action (not using parameter)
        :type force_update: bool
        :param force_update: if True, update bridge even if its already in desired version (applicable only with action=True)
        """

        # check all relevant GWs are online
        if gws_list is not None:
            assert self.check_gw_online(gws_list), 'not all gateways are online!'

        # create list of relevant gateway types for firmware update (from specified gws)
        gateway_types = {}
        for gw in gws_list:
            gw_type = self.get_gateway_type(gw)
            if gw_type not in gateway_types.keys():
                gateway_types[gw_type] = []
            gateway_types[gw_type].append(gw)

        desired_version_dict = {}
        if not update_to_latest:
            for gw_type in gateway_types:
                desired_version_dict[gw_type] = self.get_firmware_version(gw_type, desired_version, include_beta)
        else:
            if desired_version is not None:
                raise ValueError(
                    'Cannot update to latest if desired version is specified, change desired_version to None or update_to_latest to False')
            # propagate desired version dict with latest firmware for each gateway type
            for gw_type in gateway_types.keys():
                desired_version_dict[gw_type] = self.get_latest_firmware(gw_type, include_beta)

        # check BLE versions match
        ble_versions = []
        for gateway_type in desired_version_dict:
            ble_version = desired_version_dict[gateway_type]['bleChipSwVersion']
            if ble_version not in ble_versions:
                ble_versions.append(ble_version)
        if len(ble_versions) > 1:
            raise ValueError(f'Cannot update, mismatching BLE versions! {ble_versions}')
        else:
            desired_ble_version = ble_versions[0]

        # update gateways and skip already-updated ones
        updated_gateways = []
        for gw_type in desired_version_dict.keys():
            relevant_gws = gateway_types[gw_type].copy()
            desired_version_for_type = desired_version_dict[gw_type]['version']
            for gw in relevant_gws:
                gw_ver = self.get_gw_version(gw)
                if gw_ver == desired_version_for_type:
                    debug_print(f'No need to update GW {gw} to version {desired_version_for_type}, GW already updated')
                    relevant_gws.remove(gw)
                if len(relevant_gws) > 0:
                    debug_print(
                        f'Will Update GWs {relevant_gws} from type {gw_type} to version {desired_version_for_type}')
                    self.change_gw_config(relevant_gws, {'version': desired_version_for_type})
                    updated_gateways.extend(relevant_gws)
        for gw in updated_gateways:
            self.wait_for_gw_firm_update(gw)

        # get all bridges connected to gws
        all_connected_bridges = set()
        for gateway in gws_list:
            for brg in self.get_connected_brgs(gateway, ignore_bridges):
                all_connected_bridges.add(brg['id'])

        # check if all specified bridges are connected to gws
        if brgs_to_update is not None and action is False:
            for bridge in brgs_to_update:
                if bridge not in all_connected_bridges:
                    raise Exception(f'Cannot update bridge {bridge}, not connected to any one of specified GWs!')

        if update_all_connected_bridges:
            if brgs_to_update is None:
                brgs_to_update = set(all_connected_bridges)
                debug_print(f'Updating all connected bridges: '
                            f'{brgs_to_update}')
            else:
                raise ValueError('Change brgs_to_update to None or turn off update_all_connected_bridges')
        else:
            if brgs_to_update is not None:
                brgs_to_update = set(brgs_to_update)
                debug_print(f'Updating specified bridges: '
                            f'{brgs_to_update}')
            else:
                brgs_to_update = set()

        # remove already updated bridges from brgs_to_update_list
        for brg in brgs_to_update.copy():
            if self.is_brg_updated_to_ble_ver(brg, desired_ble_version) and not force_update:
                debug_print(f'Bridge {brg} already updated to BLE v. {desired_ble_version}!')
                brgs_to_update.remove(brg)

        # remove ignore bridges from brgs to update
        if ignore_bridges is not None:
            brgs_to_update = brgs_to_update - set(ignore_bridges)

        # update brgs OTA from gateway to desired version
        if len(brgs_to_update) > 0:
            debug_print(f'Starting OTA Process, updating {brgs_to_update} to {desired_ble_version}')
            if ignore_bridges is not None:
                debug_print(f'Ignoring bridges: {ignore_bridges}')
            self.run_ota_process(list(brgs_to_update), gws_list, ignore_bridges, action, force_update)

    def get_latest_firmware(self, gateway_type, include_beta=False):
        """
        Get dictionary of the latest firmware version
        :type gateway_type: GatewayType
        :type include_beta: bool
        :param include_beta: Whether to include beta firmware versions
        :return: dictionary of latest firmware version
        """
        versions = self.get_gateway_versions(gateway_type, include_beta)
        if len(versions) == 0:
            raise ValueError(f'No versions for GatewayType {gateway_type}, include beta:{include_beta}')
        latest = versions[0]
        for version in versions:
            if version['releasedAt'] > latest['releasedAt']:
                latest = version
        return latest

    def gws_firmware_update(self, gws_list, desired_version):
        gws_updated = True
        for gw in gws_list:
            gw_ver = self.get_gw_version(gw)
            if gw_ver != desired_version:
                gws_updated = False
        if gws_updated:
            debug_print(f'GWs already updated to {desired_version}')
        else:
            debug_print(f'Updating {gws_list} to {desired_version}')
            self.change_gw_config(gws_list, {'version': desired_version})
            for gw in gws_list:
                self.wait_for_gw_firm_update(gw)

    def run_ota_process(self, connected_bridges, gw_ids, ignore_bridges=None, action=False, force_update=False):
        """
        :type connected_bridges: list or dictionary
        :param connected_bridges: iterable object of bridges to update
        :type gw_ids: list or dictionary
        :param gw_ids: iterable object of bridges to update
        :type ignore_bridges: list or dictionary
        :param ignore_bridges: iterable object of bridges to update
        :type force_update: bool
        :param force_update: if True, update bridge even if its already in desired version (applicable only with action=True)
        """
        connected_bridges = connected_bridges if type(connected_bridges[0]) is str else \
            [b["id"] for b in connected_bridges]
        ignore_bridges = ignore_bridges if ignore_bridges is not None else []
        try:
            self.change_brg_config(connected_bridges, {"otaUpgradeEnabled": 0}, ignore_bridges=ignore_bridges)
        except KeyError as e:
            raise WiliotCloudError('Cannot do OTA with bridges! Bridge not connected to active GW')
        gw_ble_version = self.get_gw_ble_version(gw_ids[0])
        total_time_for_updates = 0
        for idx in range(1, len(gw_ids)):
            if self.get_gw_ble_version(gw_ids[idx]) != gw_ble_version:
                debug_print("Error: not all gateways on the same BLE version")
                sys.exit()
        # Update of BRG FW should take ~3-15 min
        chances_times = [5, 5, 10]  # times for trying to update
        total_success = [0] * len(connected_bridges)
        for time_idx in range(len(chances_times)):
            if 0 not in total_success:
                debug_print("All bridges were updated, will continue now")
                break
            trying_time = chances_times[time_idx]
            debug_print("Starting upgrade iteration number {}, will try all bridges that were not upgraded yet "
                        "with timeout of {} minutes".format(time_idx, trying_time))
            for idx, brg in enumerate(connected_bridges):
                if total_success[idx] == 1:
                    continue
                debug_print(SEP)
                if brg in ignore_bridges:
                    debug_print("Ignoring bridge {}".format(brg))
                    total_success[idx] = 1
                    continue
                if gw_ble_version == self.get_brg_ble_version(brg) and not force_update:
                    debug_print("Both GW BLE and BRG versions are {}, no need to update bridge {}".format(
                        gw_ble_version, brg))
                    total_success[idx] = 1
                else:
                    debug_print("Trying to update bridge {} ({}/{})".format(brg, idx + 1, len(connected_bridges) -
                                                                            len(ignore_bridges)))
                    if action:
                        self.do_action_ota(gw_ids[0], brg)
                    else:
                        self.change_ota(brg, 1)

                    debug_print("Giving {} minutes before moving to the next bridge".format(trying_time))
                    add_time, success = self.do_ota(trying_time, brg, gw_ble_version)
                    total_time_for_updates += add_time
                    total_success[idx] = 1 if success else 0

                    if not action:
                        self.change_ota(brg, 0)
        for idx, brg in enumerate(connected_bridges):
            if total_success[idx] == 0:
                debug_print("Upgrading bridge {} failed!!! please check it physically".format(brg))

        brg_list_connected = []
        for i in range(len(gw_ids)):
            brg_list_connected += self.get_connected_brgs(gw_ids[i], ignore_bridges=ignore_bridges)
        brg_list_connected = [b["id"] for b in brg_list_connected]
        for idx, brg in enumerate(connected_bridges):
            if brg not in brg_list_connected:
                debug_print("bridge {} is no longer connected after the OTA upgrade".format(brg))

    def get_firmware_version(self, gateway_type, version, include_beta=False):
        """
        Get dictionary of specified firmware version
        :type gateway_type: GatewayType
        :param version: version to get dictionary of
        :rtype: dict
        :return: dictionary of firmware version
        """
        versions = self.get_gateway_versions(gateway_type, include_beta=include_beta)
        for v in versions:
            if v['version'] == version:
                return v
        debug_print(f'version {version} not available for {gateway_type}, available versions: ')
        self.print_available_versions(include_beta=include_beta)
        raise ValueError(f'version {version} not available for {gateway_type}!')

    def print_available_versions(self, include_beta):
        for gw_type in {GatewayType.WIFI, GatewayType.LTE}:
            debug_print(gw_type.value, center=True)
            versions = self.get_gateway_versions(gateway_type=gw_type, include_beta=include_beta)
            for version in versions:
                version['releasedAt'] = mstimestamp_to_timezone(version['releasedAt'], hour=False)
            debug_print('\n' + tabulate.tabulate(versions, headers="keys"))

    def do_ota(self, num_of_min, brg, gw_ble_version, sleep_time=10):
        """
        :type num_of_min: int
        :param num_of_min: num of minutes for trying to ota_upgrade
        :type brg: string
        :param brg: bridge to upgrade (from connected_bridges) ID
        :type gw_ble_version: string
        :param gw_ble_version: version to upgrade the bridge to
        :type sleep_time: int
        :param sleep_time: num of seconds between checks if the version has been updated
        :return: time in seconds spent in this function And True if successful False otherwise
        """
        # brg = brg if type(brg) is str else brg["id"]
        itter = int(60 / sleep_time * num_of_min) if num_of_min != 0 else 1
        for i in range(itter):
            self.ota_sleep(sleep_time)
            is_updated = False
            try:
                is_updated = self.is_version_updated(int((i + 1) * sleep_time), gw_ble_version, brg, int(60 * num_of_min))
            except WiliotCloudError as e:
                print(f'Exception {e}')
            if is_updated:
                return int((i + 1) * sleep_time), True
        return int(itter * sleep_time), False

    def change_ota(self, brg_id, val, action=False):
        """
        changes ota_enable
        :type brg_id: str
        :param brg_id: bridge id
        :type val: int
        :param val: 0/1
        """
        brg_keys = self.get_bridge(brg_id)["config"].keys()
        if 'otaUpgradeEnabled' not in brg_keys:
            print(f'Cannot update OTA for bridge {brg_id}, otaUpgradeEnabled not in configuration parameters!')
            return None
        self.change_brg_config([brg_id], {"otaUpgradeEnabled": val}, minutes_timeout=30)
    
    def do_action_ota(self, gw_id, brg_id):
        """
        does OTA using action API
        :param gw_id: GW id
        :param brg_id: BRG id
        """
        assert self.get_gateway_type(gw_id) == GatewayType.WIFI
        debug_print(f'Sending REBOOT to brg {brg_id}')
        res = self.send_bridge_action_through_gw(gw_id, BridgeThroughGatewayAction.REBOOT, payload='000', bridge_id=brg_id)
        time.sleep(3)
        debug_print(f'Initializing DFU W/ GW {gw_id} to BRG {brg_id}')
        res = self.send_action_to_gateway(gw_id, GatewayAction.START_BRIDGE_OTA, bridge_id=brg_id)

    def wait_for_gw_firm_update(self, gw_id):
        gw = self.get_gateway(gw_id)
        while gw['online'] is False:
            debug_print('Waiting for GW to get back online...')
            sleep(10)
            gw = self.get_gateway(gw_id)
        reported = gw['reportedConf']['bleChipSwVersion']
        desired = gw['desiredConf']['bleChipSwVersion']
        cnt = 0
        while reported != desired and cnt < 30:
            debug_print(f'Desired BLE: {desired}, Reported BLE: {reported}, Waiting for GW to update')
            sleep(10)
            gw = self.get_gateway(gw_id)
            reported = gw['reportedConf']['bleChipSwVersion']
            desired = gw['desiredConf']['bleChipSwVersion']
            cnt = cnt + 1
        if reported == desired:
            debug_print('GW {} Version {}'.format(gw_id, gw['reportedConf']['version']))
        else:
            debug_print(f'Could not update GW {gw_id} to version!')
            raise WiliotCloudError(f'Could not update GW {gw_id} to version!')

    def is_version_updated(self, j, gw_ble_version_internal, brg_internal, checking_time_internal):
        """
        :type j: int
        :param j: time which have been waited to get if version was updated until now
        :type gw_ble_version_internal: string
        :param gw_ble_version_internal: version to upgrade the bridge to
        :type brg_internal: string
        :param brg_internal: bridge to upgrade (from connected_bridges) ID
        :type checking_time_internal: int
        :param checking_time_internal: num of seconds between checks if the version has been updated
        :return: True if updated
        """
        brg_ver = self.get_brg_ble_version(brg_internal)
        if gw_ble_version_internal == brg_ver:
            debug_print("Bridge {} version has been updated to version {} after {} seconds, "
                        "continue to next bridge".format(brg_internal, gw_ble_version_internal, j))
            return True
        else:
            if j < checking_time_internal:
                debug_print("Bridge {} version ({}) has not been updated to version {} after {} seconds, "
                            "will stop trying after {} seconds".format(brg_internal,
                                                                       self.get_brg_ble_version(brg_internal),
                                                                       gw_ble_version_internal, j,
                                                                       checking_time_internal))
            else:
                debug_print("Bridge {} has failed to update to version {} after {} seconds, "
                            "continue to next bridge".format(brg_internal, gw_ble_version_internal, j))
            return False



    @staticmethod
    def ota_sleep(secs):
        """
        :type secs: int
        :param secs: seconds to wait until ota is done
        """
        chars = ["|", "/", "-", "\\"]
        for i in range(secs * 2):
            sys.stdout.write("\r" + chars[i % 4] * 20 + " " + str(i // 2) + " " + chars[i % 4] * 20)
            sys.stdout.flush()
            sleep(0.5)
        print("\n")
