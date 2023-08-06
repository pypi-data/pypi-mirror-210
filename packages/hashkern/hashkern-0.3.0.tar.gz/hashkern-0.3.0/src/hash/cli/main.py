import argparse
import configparser
import os
import sys
from hash import errors

from hash.kern import main_action, __VERSION__
from hash.kern.templates import Renderer
from hash.store import get_store
from hash.resources import ResourceSpace, get_resource


def __read_config(args):
    config = configparser.ConfigParser()
    config.read(args.config)
    sections = config.sections()
    if sections == []:
        sys.exit(9)
    return config


def build(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    return main_action(args.path, "build", args.env, os.environ["PWD"], s, args.plan)


def test(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    return main_action(args.path, "test", args.env, os.environ["PWD"], s, args.plan)


def publish(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    return main_action(args.path, "publish", args.env, os.environ["PWD"], s, args.plan)


def deploy(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    return main_action(args.path, "deploy", args.env, os.environ["PWD"], s, args.plan)


def _hash(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    rs = ResourceSpace(os.environ["PWD"], s)
    r = get_resource(args.path)
    return rs.calculate_hash(r)


def render(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    rs = ResourceSpace(os.environ["PWD"], s)
    r = get_resource(args.path)
    r = Renderer(r, rs, s, s.get_globals(), args.env)
    r.render(args.env)


def clear(args):
    configs = __read_config(args)
    try:
        config = dict(configs[args.storage])
    except KeyError:
        config = {}
    try:
        s = get_store(args.storage, config)
    except errors.StoreNotFound as e:
        print(f"Error in storage plugin {args.storage}, {e}")
        sys.exit(1)
    s.init(config)
    rs = ResourceSpace(os.environ["PWD"], s)
    r = get_resource(args.path)
    r = Renderer(r, rs, s, {}, args.env)
    r.clear()


def version(args):
    return __VERSION__


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="hash",
        description="A tool to build resources based on their hash and type",
    )
    sub_parsers = parser.add_subparsers(dest="subparser_name")
    parser.add_argument(
        "--storage",
        help="The storage system used default is Local File",
        default="LocalFile",
    )
    parser.add_argument(
        "--config",
        help="The configuration file default is config.ini",
        default="config.ini",
    )
    parser.add_argument(
        "--env", help="An environment to run the action in it", default=None
    )
    parser.add_argument(
        "--plan", help="Only do a plan and save it to this file", default=None
    )
    parser_build = sub_parsers.add_parser("build")
    parser_build.add_argument("path", help="path to build")
    parser_build.set_defaults(func=build)
    parser_test = sub_parsers.add_parser("test")
    parser_test.add_argument("path", help="path to test")
    parser_test.set_defaults(func=test)
    parser_publish = sub_parsers.add_parser("publish")
    parser_publish.add_argument("path", help="path to publish")
    parser_publish.set_defaults(func=publish)
    parser_deploy = sub_parsers.add_parser("deploy")
    parser_deploy.add_argument("path", help="path to deploy")
    parser_deploy.set_defaults(func=deploy)

    parser_hash = sub_parsers.add_parser("hash")
    parser_hash.add_argument("path", help="path to hash")
    parser_hash.set_defaults(func=_hash)

    parser_render = sub_parsers.add_parser("render")
    parser_render.add_argument("path", help="path to render")
    parser_render.set_defaults(func=render)

    parser_clear = sub_parsers.add_parser("clear")
    parser_clear.add_argument("path", help="path to clear")
    parser_clear.set_defaults(func=clear)

    parser_version = sub_parsers.add_parser("version")
    parser_version.set_defaults(func=version)

    args = parser.parse_args(argv)
    if args.subparser_name is None:
        parser.print_help()
        sys.exit(1)
    try:
        return args.func(args)
    except errors.ResourceError as e:
        return f"Error: {e}"


if __name__ == "__main__":
    output = main(sys.argv[1:])
    if output:
        print(output)
