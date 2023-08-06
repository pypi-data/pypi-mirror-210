import sys
from pathlib import Path


from .config import load_config
from .log import logger
from .utils import out_print



# 命令行确认
def confirm(prompt: str, default: bool = False) -> bool:
    """Confirm with user input"""
    if default:
        prompt = f'{prompt} (Y/n) '
    else:
        prompt = f'{prompt} (y/N) '
    while True:
        choice = input(prompt).lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False
        elif choice == '':
            return default
        else:
            print('请回答 yes 或 no.')

def script_main():
    def print_version():
        import pkg_resources
        out_print(f'salesea {pkg_resources.get_distribution("salesea").version}')

    # 命令行解析
    import argparse
    parser = argparse.ArgumentParser(
        prog='salesea',
        usage='%(prog)s [command] [options]',
        description='This is an Nginx log collection tool.',
        add_help=False
    )

    parser.add_argument(
        '-V', '--version', action='store_true',
        help='Print version and exit'
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help message and exit'
    )
    parser.add_argument(
        '-g', '--generate', action='store_true',
        help='Generate the configuration file'
    )
    parser.add_argument(
        '-s', '--start', action='store_true',
        help='Start the service'
    )
    parser.add_argument(
        '-c', '--config', type=str, default='salesea.ini',
        help='Specify the configuration file'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode'
    )
    # 预览快照
    parser.add_argument(
        '-p', '--preview', type=str,
        help='Preview the snapshot'
    )
    # 创建快照
    parser.add_argument(
        '-b', '--backup', action='store_true',
        help='Create a snapshot'
    )
    # 恢复快照 输入快照ID
    parser.add_argument(
        '-r', '--restore', type=str,
        help='Restore the snapshot'
    )
    # 查看快照
    parser.add_argument(
        '-l', '--list', action='store_true',
        help='List snapshots'
    )
    # 删除快照 输入快照ID
    parser.add_argument(
        '-x', '--delete', type=str,
        help='Delete the snapshot'
    )

    args = parser.parse_args()

    if args.help:
        print_version()
        parser.print_help()
        sys.exit()

    if args.version:
        print_version()
        sys.exit()

    if args.generate:
        from .config import generate_config
        generate_config()
        sys.exit()

    if args.debug:
        logger.setLevel('DEBUG')

    if args.start:
        load_config(args.config or None)
        from . import launch
        launch()
        sys.exit()

    from .config import NGINX_PATH
    from .nginx import Nginx
    nginx = Nginx(Path(NGINX_PATH) if NGINX_PATH else None)

    if args.preview:
        out_print('---------- 预览快照 ----------')
        configs = nginx.get_snapshot(args.preview)
        for filename, content in configs.items():
            out_print(f'# configuration file: {filename}')
            out_print(content)
        sys.exit()

    if args.backup:
        out_print('---------- 创建快照 ----------')
        nginx.save_snapshot()
        sys.exit()

    if args.restore:
        out_print('---------- 恢复快照 ----------')
        if confirm(f'请确认是否恢复快照[{args.restore}]?'):
            nginx.restore_snapshot(args.restore)
        sys.exit()

    if args.list:
        snapshots = nginx.get_snapshot_list()
        out_print('---------- 快照列表 ----------')
        if not snapshots:
            out_print('          [没有快照]')
            out_print('请使用 [salesea -b] 创建快照')
            sys.exit()
        for snapshot in snapshots:
            out_print(snapshot.get('name'))
        sys.exit()

    if args.delete:
        # 确认删除
        out_print('---------- 删除快照 ----------')
        if confirm(f'请确认是否删除快照[{args.delete}]?'):
            nginx.delete_snapshot(args.delete)
        sys.exit()

    parser.print_help()
    sys.exit()


def main():
    try:
        script_main()
    except KeyboardInterrupt:
        out_print("\n\nCtrl+C")
