from wiliot_deployment_tools.power_mgmt.power_mgmt import PowerManagementClient
from wiliot_core import check_user_config_is_ok
from wiliot_deployment_tools.common.utils_defines import *
from argparse import ArgumentParser
import sys


def main():
    # parser
    parser = ArgumentParser(prog='wlt-power-mgmt',
                            description='Power Management - CLI Tool for using Wiliot Bridge power management functionality')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    parser.add_argument('-brg', type=str, help="Bridge ID", required=True)
    parser.add_argument('-test', action='store_true',
                        help='if flag used, use test environment (prod is used by default)')

    subparsers = parser.add_subparsers()
    parser_enter = subparsers.add_parser('enter',
                                         help='Configure Specified Bridges to work in power management configuration',
                                         epilog="example usage: wlt-power-mgmt -o wiliot -brg 0123ABCD enter -sleepduration 5 -onduration 60")
    parser_enter.set_defaults(func=enter_contex)
    parser_enter.add_argument('-sleepduration', type=int, help="Sleep duration (minutes)", required=True)
    parser_enter.add_argument('-onduration', type=int, help="On duration (seconds) *rounds to nearest 30 second interval*", required=True)
    parser_enter.add_argument('-keepalive', type=int, help="Keep alive period (seconds) *rounds to nearest 5 second interval* (not required, defaults to 30 seconds)", required=False, default=KEEP_ALIVE_PERIOD)
    parser_enter.add_argument('-scan', type=int, help="Keep alive scan (milliseconds) *rounds to nearest 10 millisecond interval* (not required, defaults to 300 milliseconds)", required=False, default=KEEP_ALIVE_SCAN_DURATION)
    parser_enter.add_argument('-ledoff', action='store_false', help="Configure LEDs off (on by default)", required=False)
    parser_enter.add_argument('-gw', type=str, help="GW ID to configure bridge (required only for broadcast mode)", required=False)
    parser_enter.add_argument('-timeout', type=int, help="Minutes timeout (not required, defaults to 5 minutes)", required=False, default=5)

    parser_exit = subparsers.add_parser(
        'exit', help='Return specified bridges out of power management mode and into normal working mode',
        epilog="example usage: wlt-power-mgmt -o wiliot -brg 0123ABCD exit")
    parser_exit.set_defaults(func=exit_contex)
    parser_exit.add_argument('-gw', type=str, help="GW ID to configure bridge (not required)", required=False)
    parser_exit.add_argument('-no_config', action='store_false', help="If used, GW will not change to optimal configuration", required=False)
    parser_exit.add_argument('-timeout', type=int, help="Minutes timeout (not required, defaults to 5 minutes)", required=False, default=5)


    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args, unknown = parser.parse_known_args()
    if args.test:
        env = 'test'
    else:
        env = 'prod'
    owner_id = args.owner

    conf_env = env if env == 'prod' else 'non-prod'
    user_config_file_path, api_key, is_success = check_user_config_is_ok(
        owner_id, conf_env, 'edge')
    if is_success:
        print('credentials saved/upload from {}'.format(user_config_file_path))
    else:
        raise Exception('invalid credentials - please try again to login')

    args.pm = PowerManagementClient(api_key, owner_id, env)
    args.func(args)


def enter_contex(args):
    res = args.pm.enter_power_mgmt(args.sleepduration, args.onduration, args.keepalive, args.scan, 
                                   leds_on=args.ledoff, gateway_id=args.gw, bridge_id=args.brg, minutes_timeout=args.timeout)
    print(res)


def exit_contex(args):
    res = args.pm.exit_power_mgmt(gateway_id=args.gw, update_gw=args.no_config, 
                                  bridge_id=args.brg, minutes_timeout=args.timeout)
    print(res)

def main_cli():
    main()
if __name__ == '__main__':
    main()
