import pprint
from wiliot_deployment_tools.api.extended_api import ExtendedEdgeClient
from argparse import ArgumentParser
from wiliot_core import check_user_config_is_ok
import colorama

def main():
    parser = ArgumentParser(prog='wlt-log',
                            description='Log Viewer - CLI Tool to view Wiliot Gateway logs')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-owner', type=str, help="Owner ID", required=True)
    required.add_argument('-gw', type=str, help="Gateway ID", required=True)
    parser.add_argument('-test', action='store_true',
                    help='If flag used, use test environment (prod is used by default)')

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

    colorama.init()
    print(colorama.Fore.LIGHTBLACK_EX, end=None)
    print(colorama.Fore.GREEN +
          f'---Printing info for {args.gw}---' + colorama.Style.RESET_ALL)
    print(colorama.Style.RESET_ALL)
    e = ExtendedEdgeClient(api_key, args.owner, env)
    try:
        print_gw(e, args.gw)
    except AttributeError:
        parser.print_help()

def print_gw(e, gw):
    info = e.get_gateway_info(gw)

    print(colorama.Fore.GREEN +
        f'---Gateway Info---' + colorama.Style.RESET_ALL)
    pprint.pprint(info)
    print()
    print(colorama.Fore.GREEN +
        f'---Gateway Logs---' + colorama.Style.RESET_ALL)
    e.print_gateway_logs(gw)
    
def main_cli():
    main()


if __name__ == '__main__':
    main()
