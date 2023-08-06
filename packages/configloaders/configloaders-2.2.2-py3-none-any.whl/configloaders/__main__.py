import argparse
import importlib

from .__core import DefaultProvider, Namespace


def parse_obj(path: str):
    ps = path.split(':')
    mps, ops = ps[0], ps[1] if len(ps) > 1 else None
    module = None
    for mp in mps.split('.'):
        module = importlib.import_module(mp, module)
    obj = module
    if ops is None: return obj
    for op in ops.split('.'):
        ns = Namespace(obj)
        obj = ns[op]
    return obj


def show(args):
    ns = Namespace(parse_obj(args.target))
    if args.raw:
        print(ns.target)
    else:
        print(ns)


def update(args):
    data = {}
    ns = Namespace(parse_obj(args.target))
    for key in ns:
        data[key] = ns[key]
    DefaultProvider(args.provider).dump(data)


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers()

    show_parser = sub_parsers.add_parser('show')
    show_parser.add_argument('-t', '--target', default='config')
    show_parser.add_argument('-r', '--raw', action='store_true')
    show_parser.set_defaults(action=show)

    save_parser = sub_parsers.add_parser('save')
    save_parser.add_argument('-t', '--target', default='config')
    save_parser.add_argument('-p', '--provider', default='json')
    save_parser.set_defaults(action=update)

    args = parser.parse_args()
    if not hasattr(args, 'action'):
        parser.print_help()
        exit(1)
    args.action(args)


if __name__ == '__main__':
    main()
