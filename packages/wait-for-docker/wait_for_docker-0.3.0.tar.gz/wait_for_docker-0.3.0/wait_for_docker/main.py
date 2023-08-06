"""Wait for Docker to be active."""
import argparse
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass

import docker
from docker.errors import DockerException
from yaspin import yaspin

from wait_for_docker import __version__


def main():
    args = get_args()

    if args.version:
        print(__version__)
        sys.exit()

    with exit_with_interrupt():
        with yaspin():
            while not check_docker():
                time.sleep(0.5)

        print("Docker is active now.")


@dataclass
class CliArgs:
    version: bool


def get_args() -> CliArgs:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--version", "-V", action="store_true")

    parsed = parser.parse_args()

    return CliArgs(version=parsed.version)


def check_docker() -> bool:
    try:
        docker.from_env()
    except DockerException:
        return False

    return True


@contextmanager
def exit_with_interrupt():
    try:
        yield
    except KeyboardInterrupt:
        sys.exit(1)
