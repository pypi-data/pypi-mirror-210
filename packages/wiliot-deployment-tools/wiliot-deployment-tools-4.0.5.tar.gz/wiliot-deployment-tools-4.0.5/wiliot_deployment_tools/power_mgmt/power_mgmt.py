import datetime
from doctest import debug
import sys
import time
import bitstruct
from wiliot_deployment_tools.api.extended_api import BridgeThroughGatewayAction, ExtendedEdgeClient, GatewayType
from wiliot_deployment_tools.common.debug import debug_print
from wiliot_deployment_tools.common.utils_defines import KEEP_ALIVE_PERIOD, KEEP_ALIVE_SCAN_DURATION, SEC_TO_SEND, BROADCAST_DST_MAC, EXIT_POWER_MGMT_GW_DICT


class PowerManagementError(Exception):
    pass


class PowerManagementPacket:
    def __init__(self, payload=None):
        """
        :type payload: str
        :param payload: power management packet payload (hex string)
        """
        self.payload = payload

    def __repr__(self):
        sleep_duration_mins, on_duration_secs, keep_alive_period_secs, keep_alive_scan_ms, leds_on = self.unpack()
        return f'SD[{sleep_duration_mins}]OD[{on_duration_secs}]KA_P[{keep_alive_period_secs}]KA_S[{keep_alive_scan_ms}]L[{leds_on}]'

    @classmethod
    def from_args(cls, sleep_duration_mins, on_duration_secs,
                  keep_alive_period_secs=KEEP_ALIVE_PERIOD, keep_alive_scan_ms=KEEP_ALIVE_SCAN_DURATION, leds_on=True,
                  silent=False):
        """
        Create power management packet from specified arguments
        :type sleep_duration_mins: int
        :param sleep_duration_mins: Sleep duration (minutes)
        :type on_duration_secs: int
        :param on_duration_secs: On duration (seconds) - rounds to the nearest 30 second interval
        :type keep_alive_period_secs: int
        :param keep_alive_period_secs: Keep-alive period (seconds) - rounds to the nearest 5 second interval
        :type keep_alive_scan_ms: int
        :param keep_alive_scan_ms: Keep-alive scan duration (milliseconds) - rounds to the nearest 10 millisecond interval
        :type leds_on: bool
        :param leds_on: leds on/off during power management
        :type silent: bool
        :param silent: print power management
        :rtype: PowerManagementPacket
        :return: packet of specified parameters
        """
        if keep_alive_period_secs is None:
            keep_alive_period_secs = KEEP_ALIVE_PERIOD
        if keep_alive_scan_ms is None:
            keep_alive_scan_ms = KEEP_ALIVE_SCAN_DURATION
        payload = cls.pack_pwr_mgmt_struct(sleep_duration_mins, on_duration_secs, keep_alive_period_secs,
                                           keep_alive_scan_ms, leds_on, silent)
        packet = cls(payload)
        return packet

    @classmethod
    def exit_packet(cls, silent=True):
        """
        returns packet with 0 values (to exit power management mode)
        :type silent: bool
        :param silent: print power management
        :rtype: PowerManagementPacket
        :return: packet to exit power management
        """
        return cls.from_args(sleep_duration_mins=0,
                             on_duration_secs=0,
                             keep_alive_period_secs=0,
                             keep_alive_scan_ms=0,
                             leds_on=True,
                             silent=silent)

    def unpack(self):
        return self.unpack_pwr_mgmt_packet(self.payload)

    @staticmethod
    def pack_pwr_mgmt_struct(sleep_duration_mins, on_duration_secs,
                             keep_alive_period_secs, keep_alive_scan_ms, leds_on, silent=False):
        """
        Create power management packet from specified arguments
        :type sleep_duration_mins: int
        :param sleep_duration_mins: Sleep duration (minutes)
        :type on_duration_secs: int
        :param on_duration_secs: On duration (seconds) - rounds to the nearest 30 second interval
        :type keep_alive_period_secs: int
        :param keep_alive_period_secs: Keep-alive period (seconds) - rounds to the nearest 5 second interval
        :type keep_alive_scan_ms: int
        :param keep_alive_scan_ms: Keep-alive scan duration (milliseconds) - rounds to the nearest 10 millisecond interval
        :type leds_on: bool
        :param leds_on: leds on/off during power management
        :type silent: bool
        :param silent: print power management packet parameters
        :rtype: str
        :return: hex string of packet
        """
        if sleep_duration_mins != 0 and on_duration_secs != 0:
            assert keep_alive_period_secs < sleep_duration_mins * 60, 'Keep alive period must be shorter than sleep period!'
        if not 0 <= sleep_duration_mins <= 2047:
            raise PowerManagementError('Sleep Duration (minutes) must be a value between 0 and 2047!')
        if not 0 <= on_duration_secs <= 3810:
            raise PowerManagementError('On Duration (seconds) must be a value between 0 and 3810!')
        if not 0 <= keep_alive_period_secs <= 155:
            raise PowerManagementError('Keep Alive Period (seconds) must be a value between 0 and 155!')
        if not 0 <= keep_alive_scan_ms <= 630:
            raise PowerManagementError('Keep Alive Scan (milliseconds) must be a value between 0 and 630!')

        sleep_duration = sleep_duration_mins
        on_duration = int(on_duration_secs / 30)
        keep_alive_period = int(keep_alive_period_secs / 5)
        keep_alive_scan = int(keep_alive_scan_ms / 10)
        if sleep_duration != 0 and on_duration == 0 and keep_alive_period == 0:
            raise PowerManagementError('Please set keep alive period!')

        if not silent:
            debug_print(f'''Configuring Power Management:
                  Sleep Duration: {sleep_duration} minutes
                  On Duration: {on_duration * 30} seconds
                  Keep Alive Period: {keep_alive_period * 5} seconds
                  Keep Alive Scan: {keep_alive_scan * 10} milliseconds
                  LEDs: {'ON' if leds_on else 'OFF'}
                  ''')

        fmt = 'p2 b1 u6 u5 u7 u11'
        assert 0 <= keep_alive_scan <= 63
        assert 0 <= keep_alive_period <= 31
        assert 0 <= on_duration <= 127
        assert 0 <= sleep_duration <= 2047
        payload = bitstruct.pack(fmt,
                                 leds_on,
                                 keep_alive_scan,
                                 keep_alive_period,
                                 on_duration,
                                 sleep_duration).hex().upper()

        return payload

    @staticmethod
    def unpack_pwr_mgmt_packet(payload):
        """
        unpack packet to arguments
        :type payload: str
        :param payload: hex string of packet
        :rtype: tuple
        :return: (sleep_duration_mins, on_duration_secs, keep_alive_period_secs, keep_alive_scan_ms, leds_on)
        """
        assert len(payload) >= 8
        payload = payload[:8]
        payload = bytes.fromhex(payload)
        fmt = 'p2 b1 u6 u5 u7 u11'
        leds_on, keep_alive_scan, keep_alive_period, on_duration, sleep_duration = \
            bitstruct.unpack(fmt, payload)
        sleep_duration_mins = sleep_duration
        on_duration_secs = on_duration * 30
        keep_alive_period_secs = keep_alive_period * 5
        keep_alive_scan_ms = keep_alive_scan * 10
        return sleep_duration_mins, on_duration_secs, keep_alive_period_secs, keep_alive_scan_ms, leds_on


class PowerManagementClient(ExtendedEdgeClient):
    
    def check_gw_compatible_for_pwr_mgmt(self, gateway_id):
        """
        checks if gateway is compatible to send and receive power management configurations
        :type gateway_id: str
        :param gateway_id: gateway ID
        :rtype: bool
        """
        gateway_type = self.get_gateway_type(gateway_id)
        if gateway_type != GatewayType.WIFI:
            debug_print(gateway_type)
            return False
        gw_dict = self.get_gateway(gateway_id)        
        ble_ver = gw_dict["reportedConf"]["bleChipSwVersion"]
        if gw_dict['online'] and \
           self.check_ble_power_mgmt_support(ble_ver):
            if gw_dict['reportedConf']['additional']['gwMgmtMode'] == 'transparent':
                support = self.check_gw_ble_transparent_power_mgmt_support(ble_ver)
                if not support:
                    debug_print(f'Please update GW {gateway_id} or change to active mode for power management support!')
                return support
            return True
        return False


    def get_bridge_relevant_gw(self, bridge_id):
        """
        Returns relevant GW for sending actions to bridge
        :param bridge_id: Bridge ID
        :rtype: str
        :return: relevant Gateway ID
        """

        # TODO - return list of potential GWs
        potential_gws = list()
        owner_gws = self.get_gateways()
        owner_gw_ids = []
        owner_gw_ids.extend(g['gatewayId'] for g in owner_gws)
        for gw in self.get_bridge(bridge_id)['connections']:
            if gw['gatewayId'] not in owner_gw_ids:
                continue
            gw_id = gw['gatewayId']
            gw_dict = self.get_gateway(gw_id)
            if gw['connected'] and \
                    bridge_id in self.get_seen_bridges(gw_id) and \
                    self.check_gw_compatible_for_pwr_mgmt(gw_id):
                if bridge_id in self.get_seen_bridges(gw['gatewayId']):
                            return gw['gatewayId']
        raise PowerManagementError(f'No relevant GW connected to bridge! Check deployment')

    def get_relevant_bridges(self, gateway_id):
        """
        Returns seen bridges by gateway that are associated to owner and have ble version with power management support
        :type gateway_id: str
        :param gateway_id: gateway ID
        :rtype: list
        :return: list of relevant bridge IDs
        """
        bridges = self.get_seen_bridges(gateway_id)
        relevant_bridges = bridges
        for bridge in bridges:
            brg_ble = self.get_brg_ble_version(bridge)
            if not self.check_ble_power_mgmt_support(brg_ble):
                # debug_print(f'Bridge {bridge} does not support power management!')
                relevant_bridges.remove(bridge)
        return relevant_bridges


    @staticmethod
    def check_ble_power_mgmt_support(ble_ver):
        """
        checks if power management is supported for BLE version
        :rtype: bool
        :return: True if supported, False otherwise
        """
        ble_ver = ble_ver.split('.')
        if not ((int(ble_ver[0]) > 3) or
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 11) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 10 and int(ble_ver[2]) > 39)):
            return False
        else:
            return True
    
    @staticmethod
    def check_gw_ble_transparent_power_mgmt_support(ble_ver):
        """
        checks if power management is supported for transparent GW BLE version
        :rtype: bool
        :return: True if supported, False otherwise
        """
        ble_ver = ble_ver.split('.')
        if not ((int(ble_ver[0]) > 3) or
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 14) or \
                (int(ble_ver[0]) > 2 and int(ble_ver[1]) > 13 and int(ble_ver[2]) > 27)):
            return False
        else:
            return True


    def send_pwr_mgmt_pkt(self, bridge_id, packet, gateway_id=None,
                          silent=False, seconds_to_send=1):
        """
        send power management packet to bridge
        :type bridge_id: str
        :param bridge_id: Bridge ID
        :type packet: PowerManagementPacket
        :param packet: packet to send to bridge
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type silent: bool
        :param silent: print power management packet parameters
        :type seconds_to_send: int
        :param seconds_to_send: seconds to repeat packet
        :rtype: bool
        :return: True if sent, False otherwise
        """
        if gateway_id is None:
            via_gw = self.get_bridge_relevant_gw(bridge_id)
        else:
            via_gw = gateway_id
        brg_version = None
        if bridge_id is not BROADCAST_DST_MAC:
            brg_version = self.get_brg_ble_version(bridge_id)
        gw_version = self.get_gw_ble_version(via_gw)
        for version in filter(None, [brg_version, gw_version]):
            if not self.check_ble_power_mgmt_support(version):
                return False
        rxtx = datetime.timedelta(milliseconds=
                                  self.get_gateway(via_gw)['reportedConf']['additional']['rxTxPeriodMs'])
        seconds_to_send = datetime.timedelta(seconds=seconds_to_send)
        reps = seconds_to_send // rxtx + 1
        if not silent:
            debug_print(f'Sending packet through GW {via_gw} for {seconds_to_send.total_seconds()} seconds, rxTx = {int(rxtx.total_seconds()*1000)} ms, reps = {reps}')
        res = self.send_bridge_action_through_gw(gateway_id,
                                                 BridgeThroughGatewayAction.POWER_MGMT,
                                                 packet.payload, bridge_id, reps=reps)
        return res

    def broadcast_pwr_mgmt_packet(self, packet, gateway_id, silent=False, seconds_to_send=1):
        """
        broadcast packet to all bridges connected to GW
        :type packet: PowerManagementPacket
        :param packet: packet to broadcast
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type silent: bool
        :param silent: print power management packet parameters
        :rtype: tuple
        :return: results (bool), bridges sent to (list)
        """
        if not self.check_gw_compatible_for_pwr_mgmt(gateway_id):
            raise PowerManagementError(f'Gateway {gateway_id} not compatible with power management! '
                                       f'Try to update GW version')
        brgs_to_broadcast = self.get_relevant_bridges(gateway_id)
        if not silent:
            debug_print(f'Broadcasting Packet to bridges {brgs_to_broadcast}')
        res = self.send_pwr_mgmt_pkt(BROADCAST_DST_MAC, packet, gateway_id, silent, seconds_to_send)
        return res, brgs_to_broadcast

    def check_pwr_mgmt_received(self, gateway_id, bridge_id, packet, time_sent):
        """
        check if power management packet was received by bridge
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type bridge_id: str
        :param bridge_id: Bridge ID
        :type packet: PowerManagementPacket
        :param packet: packet to check
        :type time_sent: datetime
        :param time_sent: time packet was sent
        :rtype bool
        :return: True if packet was received, None otherwise
        """
        hours_back = (datetime.datetime.now() - time_sent + datetime.timedelta(seconds=5)).total_seconds() / 3600
        acks = self.get_acks(gateway_id, hours_back)
        if acks is None:
            return None
        acks = acks[(acks['actionType'] == BridgeThroughGatewayAction.POWER_MGMT) &
                    (acks['bridgeId'] == bridge_id) &
                    (acks['payload'].apply(lambda x: PowerManagementPacket(x[:8]).payload)
                     == packet.payload)]
        if len(acks) > 0:
            return acks.to_dict()
        return None

    def check_pwr_mgmt_broadcast_received(self, gateway_id, bridges, packet, time_sent):
        """
        check if power management broadcast was received by bridges
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type bridges: list
        :param bridges: list of Bridge IDs
        :type packet: PowerManagementPacket
        :param packet: packet to check
        :type time_sent: datetime
        :param time_sent: time packet was sent
        :rtype: dict
        :return: dict of bridgeIDs:received status
        """
        hours_back = (datetime.datetime.now() - time_sent + datetime.timedelta(seconds=10)).total_seconds() / 3600
        acks = self.get_acks(gateway_id, hours_back)
        result = dict().fromkeys(bridges)
        for brg in bridges:
            if acks is None:
                result[brg] = False
                continue
            brg_acks = acks[(acks['actionType'] == BridgeThroughGatewayAction.POWER_MGMT) &
                        (acks['bridgeId'] == brg) &
                        (acks['payload'].apply(lambda x: PowerManagementPacket(x[:8]).payload)
                         == packet.payload)]
            if len(brg_acks) > 0:
                result[brg] = True
            else:
                result[brg] = False
        return result

    def send_packet_until_ack(self, gateway_id, bridge_id, packet, minutes_timeout=3):
        """
        send power management packet repeatedly until it is received by the bridge
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type bridge_id: str
        :param bridge_id: Bridge ID
        :type packet: PowerManagementPacket
        :param packet: packet to send
        :type minutes_timeout: int
        :param minutes_timeout: timeout
        :rtype: dict
        :return: dict of {bridgeID: ack status (bool)} pairs
        """
        time_sent = datetime.datetime.now()
        debug_print(f'Configuring {bridge_id} To {packet} | Max Waiting time {minutes_timeout} minutes')
        self.send_pwr_mgmt_pkt(bridge_id, packet, gateway_id, silent=False, seconds_to_send=SEC_TO_SEND)
        time_gw_stops = time_sent + datetime.timedelta(seconds=SEC_TO_SEND)
        time_end = time_sent + datetime.timedelta(minutes=minutes_timeout)
        curr_time = time_sent
        ack = self.check_pwr_mgmt_received(gateway_id, bridge_id, packet, time_sent)
        print('Waiting For Ack...', end='', flush=True)
        while curr_time < time_end and ack is None:
            curr_time = datetime.datetime.now()
            if curr_time > time_gw_stops - datetime.timedelta(seconds=1):  # 1 second buffer
                self.send_pwr_mgmt_pkt(bridge_id, packet, gateway_id, silent=True, seconds_to_send=SEC_TO_SEND)
                time_gw_stops = datetime.datetime.now() + datetime.timedelta(seconds=SEC_TO_SEND)
                print('!', end='')
                sys.stdout.flush()
            time.sleep(0.5)
            print('.', end='')
            sys.stdout.flush()
            ack = self.check_pwr_mgmt_received(gateway_id, bridge_id, packet, time_sent)
        print()  # enter newline
        ack_received = False
        if ack is not None:
            ack_received = True
            debug_print(f'Ack Received after {datetime.datetime.now() - time_sent}')
        else:
            debug_print(f'Ack not received after {datetime.datetime.now() - time_sent}!')
        return {bridge_id: ack_received}

    def broadcast_packet_until_ack(self, gateway_id, packet, minutes_timeout=3):
        """
        send power management packet repeatedly until it is received by the all 'seen' bridges
        :type gateway_id: str
        :param gateway_id: Gateway ID
        :type packet: PowerManagementPacket
        :param packet: packet to send
        :type minutes_timeout: int
        :param minutes_timeout: timeout
        :rtype: dict
        :return: dict of {bridgeID: ack status (bool)} pairs
        """
        time_sent = datetime.datetime.now()
        res, bridges = self.broadcast_pwr_mgmt_packet(packet, gateway_id, silent=False, seconds_to_send=SEC_TO_SEND)
        debug_print(f'Configuring {bridges} To {packet} | Max Waiting time {minutes_timeout} minutes')
        time_gw_stops = time_sent + datetime.timedelta(seconds=SEC_TO_SEND)
        time_end = time_sent + datetime.timedelta(minutes=minutes_timeout)
        curr_time = time_sent
        ack = self.check_pwr_mgmt_broadcast_received(gateway_id, bridges, packet, time_sent)
        print('Waiting For Ack...', end='', flush=True)
        while curr_time < time_end and not all(ack.values()):
            curr_time = datetime.datetime.now()
            if curr_time > (time_gw_stops - datetime.timedelta(seconds=1)):  # 1 second buffer
                new_bridges = self.get_relevant_bridges(gateway_id)
                if bridges != new_bridges:
                    bridges = new_bridges
                    debug_print(f'Bridges seen by GW changed while broadcasting! now broadcasting to {bridges}')
                self.broadcast_pwr_mgmt_packet(packet, gateway_id, silent=True, seconds_to_send=SEC_TO_SEND)
                time_gw_stops = datetime.datetime.now() + datetime.timedelta(seconds=SEC_TO_SEND)
                print('!', end='')
                sys.stdout.flush()
            time.sleep(0.5)
            print('.', end='')
            sys.stdout.flush()
            ack = self.check_pwr_mgmt_broadcast_received(gateway_id, bridges, packet, time_sent)
        print()  # enter newline
        if not all(ack.values()):
            # list of bridges which did not return ack
            brgs_missed = list(dict(filter(lambda x: x[1] is False, ack.items())).keys())
            debug_print(f'Packet not received by bridges {brgs_missed} after {minutes_timeout} minutes!')
        else:
            debug_print(
                f'Ack Received after {datetime.datetime.now() - time_sent} by bridges {list(ack.keys())}')
        return ack

    def enter_power_mgmt(self, sleep_duration_mins, on_duration_secs, keep_alive_period_secs=None,
                         keep_alive_scan_ms=None, leds_on=True, gateway_id=None, bridge_id=None, broadcast=False,
                         minutes_timeout=3):
        """
        Enter power management mode with the specified parameters.
        Function will search for the relevant gateway ID (if not specified) to send the configuration packet through.
        :type sleep_duration_mins: int
        :param sleep_duration_mins: Sleep duration (minutes)
        :type on_duration_secs: int
        :param on_duration_secs: On duration (seconds) - rounds to the nearest 30 second interval
        :type keep_alive_period_secs: int
        :param keep_alive_period_secs: Keep-alive period (seconds) - rounds to the nearest 5 second interval.
        Defaults to 30 seconds
        :type keep_alive_scan_ms: int
        :param keep_alive_scan_ms: Keep-alive scan duration (milliseconds) - rounds to the nearest 10 millisecond interval.
        Defaults to 150 milliseconds
        :type leds_on: bool
        :param leds_on: leds on/off during power management
        :type gateway_id: str
        :param gateway_id: Gateway ID (optional)
        :type bridge_id: str
        :param bridge_id: Bridge ID
        :type broadcast: bool
        :param broadcast: if True, broadcast power mgmt to all 'seen' bridges
        :type minutes_timeout: int
        :param minutes_timeout: minutes timeout
        :rtype: dict
        :return: dict of {bridgeID: ack status (bool)} pairs
        """
        packet = PowerManagementPacket.from_args(sleep_duration_mins=sleep_duration_mins,
                                                 on_duration_secs=on_duration_secs,
                                                 keep_alive_period_secs=keep_alive_period_secs,
                                                 keep_alive_scan_ms=keep_alive_scan_ms,
                                                 leds_on=leds_on, silent=False)
        if not ((bridge_id is not None and broadcast is False) or (bridge_id is None and broadcast is True)):
            raise PowerManagementError('Must specify bridgeId / set broadcast to True')
        if broadcast:
            if gateway_id is None:
                raise PowerManagementError('Must specify GW ID to broadcast')
            return self.broadcast_packet_until_ack(gateway_id, packet, minutes_timeout)
        via_gw = self.get_bridge_relevant_gw(bridge_id) if gateway_id is None else gateway_id
        if not self.check_gw_compatible_for_pwr_mgmt(via_gw):
            raise PowerManagementError(f'GW {via_gw} Not compatible for power management!')
        return self.send_packet_until_ack(via_gw, bridge_id, packet, minutes_timeout)

    def exit_power_mgmt(self, gateway_id=None, update_gw=False, bridge_id=None, broadcast=False, minutes_timeout=3):
        """
        Exit power management mode (to normal bridge behavior).
        Function will search for the relevant gateway ID (if not specified) to send the configuration packet through.
        :type bridge_id: str
        :param bridge_id: Bridge ID
        :type gateway_id: str
        :param gateway_id: Gateway ID (optional)
        :type update_gw: bool
        :param update_gw: Update GW to optimal configuration to send configuration packet
        :type minutes_timeout: int
        :param minutes_timeout: minutes timeout
        :type broadcast: bool
        :param broadcast: if True, broadcast power mgmt to all 'seen' bridges
        :rtype: dict
        :return: dict of {bridgeID: ack status (bool)} pairs
        """
        packet = PowerManagementPacket().exit_packet(silent=False)
        if not ((bridge_id is not None and broadcast is False) or (bridge_id is None and broadcast is True)):
            raise PowerManagementError('Must specify bridgeId / set broadcast to True')
        if broadcast:
            if gateway_id is None:
                raise PowerManagementError('Must specify GW ID to broadcast')
        via_gw = self.get_bridge_relevant_gw(bridge_id) if gateway_id is None else gateway_id
        if not self.check_gw_compatible_for_pwr_mgmt(via_gw):
            raise PowerManagementError(f'GW {via_gw} Not compatible for power management!')
        gw_dict = self.get_gateway(via_gw)['reportedConf']['additional']
        need_to_update = False
        for param in EXIT_POWER_MGMT_GW_DICT:
            if gw_dict[param] != EXIT_POWER_MGMT_GW_DICT[param]:
                need_to_update = True
        if need_to_update and update_gw:
            debug_print('Changing GW Params to rxTxPeriod = 15 ms, gwRxChannel = Ch. 39')
            self.change_gw_config([via_gw], EXIT_POWER_MGMT_GW_DICT)
        if broadcast:
            res = self.broadcast_packet_until_ack(gateway_id, packet, minutes_timeout)
        else:
            res = self.send_packet_until_ack(via_gw, bridge_id, packet, minutes_timeout)
        if need_to_update and update_gw:
            debug_print('Finished sending exit packets, returning GW to old state')
            self.change_gw_config([via_gw], gw_dict)
        return res


