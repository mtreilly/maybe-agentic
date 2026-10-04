"""Local notes CLI. All persistence belongs to an explicitly supplied state file."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--state', type=Path, required=True)
sub = parser.add_subparsers(dest='command', required=True)
put = sub.add_parser('put')
put.add_argument('key')
put.add_argument('value')
get = sub.add_parser('get')
get.add_argument('key')
args = parser.parse_args()
state = json.loads(args.state.read_text()) if args.state.exists() else {}
if args.command == 'put':
    state[args.key] = args.value
    args.state.parent.mkdir(parents=True, exist_ok=True)
    args.state.write_text(json.dumps(state))
    print('stored')
else:
    if args.key not in state:
        parser.exit(1, 'note not found\n')
    print(state[args.key])
