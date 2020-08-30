import argparse

from controller import Controller
from config import global_config

parser = argparse.ArgumentParser()
parser.add_argument('--token_v2', required=True, help='Your notion.so page\'s token, which can be obtained by inspecting browser cookies.')
parser.add_argument('--page', required=True, help='The notion page\'s id or URL.')

if __name__ == '__main__':
    args = parser.parse_args()
    ctl = Controller(token_v2=args.token_v2, config=global_config)
    ctl.get_serializer(ctl.notion_cli.get_block(args.page)).write()
