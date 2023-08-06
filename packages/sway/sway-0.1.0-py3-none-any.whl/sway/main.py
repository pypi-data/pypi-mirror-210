from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(prog="sway")

    # subparsers
    subparsers = parser.add_subparsers(dest="command")
    config_parser = subparsers.add_parser(
        "config",
        help=".pymonorepo-config.yaml options",
    )
    branch_parser = subparsers.add_parser(
        "branch",
        help="branch-management options",
    )
    build_parser = subparsers.add_parser(
        "build",
        help="build-management options",
    )

    # branch subparser commands
    branch_parser.add_argument(
        "--environment",
        "-E",
        required=True,
        help="Project name setup in ~/.aws/.awsslack-config.yaml",
    )

    args = parser.parse_args()

    if args.command == "branch":
        return 

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

