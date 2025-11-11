from __future__ import annotations

import argparse
import datetime
import pathlib
import sys

from . import build, models, serve


def main():
    parser = argparse.ArgumentParser(
        prog="writober", description="Build the writober website"
    )
    parser.add_argument("--source", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument(
        "--destination", type=pathlib.Path, default=pathlib.Path.cwd() / "_build"
    )
    parser.add_argument("--until", type=datetime.date.fromisoformat)
    subparsers = parser.add_subparsers(required=True)
    build_command = subparsers.add_parser("build")
    build_command.set_defaults(command=build_website)

    serve_command = subparsers.add_parser("serve")
    serve_command.set_defaults(command=serve_website)

    namespace = parser.parse_args(sys.argv[1:])
    settings = models.Settings.from_pyproject(
        args=models.Args(
            source_dir=namespace.source,
            build_dir=namespace.destination,
            provided_until=namespace.until,
        )
    )
    namespace.command(settings)


def build_website(settings: models.Settings):
    build.build(settings=settings)


def serve_website(settings: models.Settings):
    serve.serve(settings=settings)


if __name__ == "__main__":
    main()
