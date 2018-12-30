import argparse

parser = argparse.ArgumentParser(description='Jian Dao Yun Push Tool')
parser.add_argument('--debug', help='enable debug mode', action="store_true")
parser.add_argument('--sync', '-s', help='run sync', action='store_true')
parser.add_argument('--daemon', '-d', help='run as daemon', action='store_true')
args = parser.parse_args()

if args.daemon and args.sync:
    parser.error('只能使用单一运行方式')
    exit(1)

if not args.daemon and not args.sync:
    parser.error('请指定运行方式: sync/daemon')
    exit(1)
