from argparse import ArgumentParser
import sys

from wiliot_core import check_user_config_is_ok
from wiliot_deployment_tools.firmware_update.firmware_update import FirmwareUpdate
from wiliot_deployment_tools.common.debug import debug_print
def main():
    parser = ArgumentParser(prog='wlt-firmware',
                            description='Firmware Update - CLI Tool for updating Wiliot Gateways and Bridges firmware OTA')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    parser.add_argument('-test', action='store_true',
                        help='If flag used, use test environment (prod is used by default)')
    parser.add_argument('-beta', action='store_true', help="Show available beta versions / update to beta firmware",
                               required=False)
    subparsers = parser.add_subparsers()

    parser_versions = subparsers.add_parser('versions', help='Display available versions',
                                            description='Prints all avaliable Firmware versions for update for every GW Type',
                                            epilog="example usage: wlt-firmware -o wiliot versions")
    parser_versions.set_defaults(func=print_versions)

    parser_update = subparsers.add_parser('update', help='Update Gateways and Bridges',
                                          description=' Run OTA Process, first updating specified GWs to latest / specified FW version. Afterwards seuqentially update each specified Bridges / all Bridges to the same Firmware version.',
                                          epilog="example usage: wlt-firmware -o wiliot update -gw GW0123 -all_brgs")
    parser_update.set_defaults(func=firmware_update)
    parser_update.add_argument('-version', type=str,
                               help="Desired version. If not specified, will update to latest available version",
                               required=False)
    parser_update.add_argument('-gw', nargs='+', help="Gateways to update (multiple allowed)", required=False)
    parser_update.add_argument('-brg', nargs='+', help="Bridges to update (multiple allowed)", required=False)
    parser_update.add_argument('-all_brgs', action='store_true', help="Update all bridges connected to Gateways", required=False)
    parser_update.add_argument('-ignore_bridges', nargs='+', required=False, help='Bridges to ignore')
    parser_update.add_argument('-action', action='store_true', help="Update using action API",
                               required=False)
    # parser_update.add_argument('-force', action='store_true',
    #                            help='update bridge even if its already in desired version (applicable only with -action)')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
        
    args = parser.parse_args()
    if args.test:
        env = 'test'
    else:
        env = 'prod'
    owner_id = args.owner
    conf_env = env if env == 'prod' else 'non-prod'
    user_config_file_path, api_key, is_success = check_user_config_is_ok(owner_id, conf_env, 'edge')
    if is_success:
        print('credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid credentials - please try again to login')

    args.fw = FirmwareUpdate(api_key, owner_id, env)
    if 'func' not in args.__dict__:
        debug_print('Wrong Usage! please specify positional arguments')
        parser.print_help()
        sys.exit()
    args.func(args)


def firmware_update(args):
    # get specified GW types
    args.latest = True if args.version is None else False
    args.fw.firmware_update(gws_list=args.gw,
                             brgs_to_update=args.brg,
                             update_all_connected_bridges=args.all_brgs,
                             desired_version=args.version,
                             update_to_latest=args.latest,
                             include_beta=args.beta,
                             ignore_bridges=args.ignore_bridges,
                             action=args.action)
                            #  force_update=args.force)

def print_versions(args):
    args.fw.print_available_versions(args.beta)

def main_cli():
    main()

if __name__ == "__main__":
    main()
