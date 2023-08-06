from math import exp
import sys
from wiliot_deployment_tools.automatic_configuration_tool.automatic_configuration_tool import AutomaticConfigurationTool
from argparse import ArgumentParser
from wiliot_core import check_user_config_is_ok


def main():
    parser = ArgumentParser(prog='wlt-config', 
                            description='Automatic Configuration Tool - CLI Tool to automatically configure Wiliot deployments',
                            epilog='example usage: wlt-config -owner wiliot -location "My Deployment" -ota -pacing_interval 10 -ignore_bridges 1234ABCD0123')
    
    # Required Arguments
    required = parser.add_argument_group('required arguments')
    required.add_argument("-owner", type=str, help="Platform owner id", required=True)
    required.add_argument("-location", type=str, help="Location name in Wiliot platform. If location has ' ' in name, input location wrapped with double quotes: -location \"LOCATION NAME\" ", required=True)
    
    # Optional Arguments
    optional = parser.add_argument_group('additional (optional) arguments')
    optional.add_argument("-ota", action='store_true', help="Updating FW version to latest for all devices")
    optional.add_argument("-no_gp_zone", action='store_false',
                        help="Don't use global pacing group by zone (all bridges will be GPG=0)")
    optional.add_argument("-pacer", type=int, help="Pacing interval for all devices", default=15)
    optional.add_argument("-ignore_bridges", type=str, help="Bridges to ignore in the tool - their configuration won't "
                                                           "be changed", nargs="*", default=[])
    optional.add_argument('-expected_num_brgs', type=int, help='Number of expected bridges in location. The tool will try to connect to all bridges (excluding those specified in ignore bridges) until reaching expected number.', required=False)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    user_config_file_path, asset_api_key, is_success = check_user_config_is_ok(args.owner, 'prod', 'asset')
    if is_success:
        print('Asset Management credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid Asset Management credentials - please try again to login')
    user_config_file_path, edge_api_key, is_success = check_user_config_is_ok(args.owner, 'prod', 'edge')
    if is_success:
        print('Edge Management credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid Edge Management credentials - please try again to login')

    act = AutomaticConfigurationTool(edge_api_key=edge_api_key, asset_api_key=asset_api_key, owner=args.owner,
                                     location=args.location, env='prod', ota_upgrade=args.ota,
                                     ignore_bridges=args.ignore_bridges, pacing_interval=args.pacer,
                                     use_gp_zone=args.no_gp_zone, expected_num_brgs=args.expected_num_brgs)
    act.init_stage()

def main_cli():
    main()

if __name__ == '__main__':
    main()

