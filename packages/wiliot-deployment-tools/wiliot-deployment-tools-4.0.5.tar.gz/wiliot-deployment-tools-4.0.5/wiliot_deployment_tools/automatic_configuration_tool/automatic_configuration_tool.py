"""
  Copyright (c) 2016- 2023, Wiliot Ltd. All rights reserved.

  Redistribution and use of the Software in source and binary forms, with or without modification,
   are permitted provided that the following conditions are met:

     1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     2. Redistributions in binary form, except as used in conjunction with
     Wiliot's Pixel in a product or a Software update for such product, must reproduce
     the above copyright notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the distribution.

     3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
     may be used to endorse or promote products or services derived from this Software,
     without specific prior written permission.

     4. This Software, with or without modification, must only be used in conjunction
     with Wiliot's Pixel or with Wiliot's cloud service.

     5. If any Software is provided in binary form under this license, you must not
     do any of the following:
     (a) modify, adapt, translate, or create a derivative work of the Software; or
     (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
     discover the source code or non-literal aspects (such as the underlying structure,
     sequence, organization, ideas, or algorithms) of the Software.

     6. If you create a derivative work and/or improvement of any Software, you hereby
     irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
     royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
     right and license to reproduce, use, make, have made, import, distribute, sell,
     offer for sale, create derivative works of, modify, translate, publicly perform
     and display, and otherwise commercially exploit such derivative works and improvements
     (as applicable) in conjunction with Wiliot's products and services.

     7. You represent and warrant that you are not a resident of (and will not use the
     Software in) a country that the U.S. government has embargoed for use of the Software,
     nor are you named on the U.S. Treasury Department’s list of Specially Designated
     Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
     You must not transfer, export, re-export, import, re-import or divert the Software
     in violation of any export or re-export control laws and regulations (such as the
     United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
     and use restrictions, all as then in effect

   THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
   OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
   WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
   QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
   IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
   ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
   OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
   FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
   (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
   (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
   (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
   (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

# External Imports
from doctest import debug
import math
import os
import datetime

from appdirs import user_data_dir
import numpy as np
from collections import defaultdict

# Internal Imports
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient, ExtendedPlatformClient
from wiliot_deployment_tools.firmware_update.firmware_update import FirmwareUpdate
from wiliot_deployment_tools.common.analysis_data_bricks import create_logfile, db_utils, initialize_logger
from wiliot_deployment_tools.common.debug import debug_print, is_databricks, print_package_gitinfo
from wiliot_deployment_tools.common.utils_defines import ATC_GW_CONFIG, ATC_REGION_DICT

IS_DATABRICKS = is_databricks()


class ConfigurationToolError(Exception):
    pass


class AutomaticConfigurationTool:
    def __init__(self, edge_api_key, asset_api_key, owner, location, env='prod', ota_upgrade=False,
                 ignore_bridges=None, expected_num_brgs=None, pacing_interval=None, use_gp_zone=True, region='US'):
        """
        initialize the parameters
        :type edge_api_key: str
        :param edge_api_key: wiliot edge management API key
        :type asset_api_key: str
        :param asset_api_key: wiliot asset management API key
        :type owner: str
        :param owner: owner ID
        :type env: str
        :param env: ['prod', 'test']
        :type ota_upgrade: bool
        :param ota_upgrade: if true, updates all edge devices to the latest FW version
        :type ignore_bridges: list
        :param ignore_bridges: bridges to ignore when configuring
        :type expected_num_brgs: int
        :param expected_num_brgs: expected number of bridges in location
        :type location: str
        :param location: name of owner's location in wiliot platform
        :type pacing_interval: int
        :param pacing_interval: pacing interval to be set to bridges. defaults to 60 seconds
        :type use_gp_zone: bool
        :param use_gp_zone: if True, configures global pacing by zone (as setup in wiliot platform)
        :type region: str
        :param region: region of deployment
        """

        # Initialize logger and create export directory
        self.init_timestamp = initialize_logger()
        if IS_DATABRICKS:
            self.export_directory = f"/FileStore/shared_uploads/{db_utils().notebook.entry_point.getDbutils().notebook().getContext().userName().get()}/configtool/{self.init_timestamp}/"
            db_utils().fs.mkdirs(self.export_directory)
            self.export_directory = "/dbfs" + self.export_directory
        else:
            self.export_directory = os.path.join(user_data_dir(), 'wiliot', 'deployment_tools')

        # Print git info
        print_package_gitinfo()

        # Initialize objects
        self.edge = ExtendedEdgeClient(edge_api_key, owner, env)
        self.plat = ExtendedPlatformClient(asset_api_key, owner, env)
        self.fw_update = FirmwareUpdate(edge_api_key, owner, env)

        # Initialize parameters
        self.ota_upgrade = ota_upgrade
        self.ignore_bridges = list() if ignore_bridges is None else ignore_bridges
        self.expected_num_brgs = expected_num_brgs
        self.location = location
        self.pacing_interval = 60 if pacing_interval is None else pacing_interval
        self.use_gp_zone = use_gp_zone
        self.region = region
        if region in list(ATC_REGION_DICT.keys()):
            debug_print(f'Initialized region {region}')

        self.location_id = self.plat.get_location_id(self.location)
        if self.location_id is None:
            locations = self.plat.get_locations_names()
            raise ConfigurationToolError(f'No location named {self.location} Found! Available locations: {locations}')
            
        
        # Get bridges from location
        debug_print(f'Getting bridges from location {self.location}...')
        self.expected_bridges_dicts = self.plat.get_locations_bridges([self.location])
        self.expected_bridges_ids = [brg['bridgeId'] for brg in self.expected_bridges_dicts]
        self.expected_bridges_ids = list(set(self.expected_bridges_ids) - set(self.ignore_bridges))
        if not len(self.expected_bridges_ids) > 0:
            raise ConfigurationToolError(f'No bridges allocated to location {self.location}!')
        else:
            debug_print(f'Bridges in location {self.location}: {self.expected_bridges_ids}')
        
        # Allocate GPG numbers and create dicts
        self.gp_zones = list(set(brg['zoneId'] for brg in self.expected_bridges_dicts if 'zoneId' in brg))
        self.gp_zones_names = {}
        self.zonenum_by_brg = {}
        if self.use_gp_zone:
            debug_print('Allocating GlobalPacingGroup numbers to zones')
            for i, z in enumerate(self.gp_zones):
                self.gp_zones_names[i+1] = self.plat.get_zone(self.location_id, z)['name']
                for brg in self.expected_bridges_dicts:
                    if brg['bridgeId'] in self.ignore_bridges:
                        continue
                    if 'zoneId' in brg and brg['zoneId'] == z:
                        self.zonenum_by_brg[brg['bridgeId']] = i + 1
                    elif 'zoneId' not in brg:
                        self.zonenum_by_brg[brg['bridgeId']] = 0
            debug_print(self.gp_zones_names, pretty=True)
        else:
            self.zonenum_by_brg = {brg: 0 for brg in self.expected_bridges_ids}
        self.brgs_by_zonenum = dict()
        for brg, zone in self.zonenum_by_brg.items():
            if zone not in self.brgs_by_zonenum.keys():
                self.brgs_by_zonenum[zone] = list()
            self.brgs_by_zonenum[zone].append(brg)
            
        self.gw_ids = list(self.edge.get_gateways_from_bridges(self.expected_bridges_ids).keys())
        if len(self.gw_ids) == 0:
            raise ConfigurationToolError(f'No gateways connected to any bridge in location {self.location}!')
        self.gw_by_type = self.edge.get_gateways_types(self.gw_ids)

    def init_stage(self):
        # Change GW config
        gw_init_status = []
        self.gw_by_type = self.edge.get_gateways_types(self.gw_ids)
        for gw_type in self.gw_by_type:
            gw_init_status.extend(self.edge.change_gw_config(
                self.gw_ids, ATC_GW_CONFIG[gw_type.value]))
        if set(gw_init_status) != set(self.gw_ids):
            raise ConfigurationToolError('Cannot initialize GWs!')

        # Connect to bridges and change to brownout
        debug_print(f'Connecting to bridges in {self.location}...', center=True)
        (self.connected_bridges, self.board_type_dict) = \
            self.edge.connect_gw_bridges(expected_brgs=self.expected_bridges_ids,
                                         expected_num_brgs=self.expected_num_brgs,
                                         do_brown_out=True,
                                         minutes_timeout=2)

        # Firmware Upgrade
        if self.ota_upgrade is True:
            debug_print('Starting OTA Process...', center=True)
            self.fw_update.firmware_update(self.gw_ids, self.connected_bridges, update_to_latest=True,
                                           ignore_bridges=self.ignore_bridges, update_all_connected_bridges=False, action=True)
        
        # Configure Bridges
        debug_print('Configuring bridges...', center=True)        
        
        # Calculate Configuration Parameters
        rx_tx_cycle = max(min((2 * len(self.connected_bridges)), 255), 15)
        d_c = 0.3
        tx_cycle = math.ceil(d_c * rx_tx_cycle + 1.5)        

        num_of_tags_per_zone = defaultdict(int)
        
        # Configure bridges        
        def configure_brg_group(brg_ids, gp_group):
            online_bridges = list(set(brg_ids).intersection(set(self.connected_bridges)))
            offline_bridges = list(set(brg_ids) - set(online_bridges))
            config_dict = {"rxTxPeriodMs": rx_tx_cycle, "txPeriodMs": tx_cycle, "pacerInterval": self.pacing_interval,
                           "txProbability": 50, "energyPattern": 63,
                           "2.4GhzOutputPower": 2, "sub1GhzOutputPower": 32}
            # change dict to region
            if self.region in list(ATC_REGION_DICT.keys()):
                for key, value in ATC_REGION_DICT[self.region].items():
                    config_dict[key] = value
            
            max_tags = min(int(self.pacing_interval * 1000 / (rx_tx_cycle * 4)), 1000)
            zone_name = None
            if gp_group > 0:
                config_dict['globalPacingGroup'] = gp_group
                config_dict['txRepetition'] = 0
                max_tags = max_tags * len(brg_ids)
                zone_name = self.gp_zones_names[gp_group]
            num_of_tags_per_zone[gp_group] = max_tags
            
            # Configure offline bridges
            if len(offline_bridges) > 0:
                if zone_name is not None:
                    debug_print(f'Configuring offline bridges in zone {zone_name}')
                else:
                    debug_print(f'Configuring offline bridges')
                self.edge.change_brg_config(offline_bridges, config_dict, minutes_timeout=0)
                
            # Configure online bridges
            if len(online_bridges) > 0:
                if zone_name is not None:
                    debug_print(f'Configuring online bridges in zone {zone_name}')
                else:
                    debug_print(f'Configuring online bridges')
                res = self.edge.change_brg_config(online_bridges, config_dict, minutes_timeout=5)
                if set(res) != set(online_bridges):
                    if not all(map(self.edge.is_global_pacing_zone, (set(res)-set(online_bridges)))):
                        non_updated_bridges = list(set(online_bridges) - set(res))
                        raise ConfigurationToolError(f'Could not configure BRG {non_updated_bridges}!')
                    else:
                        non_supporting_brgs = list(set(online_bridges) - set(res))
                        debug_print(f'{non_supporting_brgs} not supporting global pacing group! please run again with ota upgrade enabled')

        for gp_group, brg_ids in self.brgs_by_zonenum.items():
            configure_brg_group(brg_ids, gp_group)
        debug_print("*************************************************", center=True)
        for zone in num_of_tags_per_zone:
            if zone in self.gp_zones_names.keys():
                zone_name = self.gp_zones_names[zone]
            else:
                zone_name = 'Unassigned (Per BRG)'
            debug_print(fr"*** - Maximum tags in zone {zone_name}: {num_of_tags_per_zone[zone]} ***", center=True)
        debug_print(fr"*** WARNING: To increase number of tags you can:***")
        debug_print(fr"***       1. Increase beacons rate priority in this zone ***")
        debug_print(fr"***       2. Increase pacingInterval in this zone ***")
        debug_print(fr"***       3. Increase number of bridges in the zone and activate globalPacing ***")
        debug_print("*************************************************", center=True)

    def create_logfile(self):
        """
        creates a log file for the current run and displays a download link in the notebook to download the file.
        """
        create_logfile(self.init_timestamp, self.export_directory, 'configtool')