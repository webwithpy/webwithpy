import sys

from .routing.router import Router
from .webwithpy import run_server
import runpy
import click
import os


@click.group()
def cli():
    """My package's command-line interface."""
    pass


def get_dirs():
    directory = os.getcwd()
    return [
        os.path.join(directory, o)
        for o in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, o))
    ]


def directory_contains_main(directory: str) -> bool:
    for entry in os.listdir(directory):
        # Construct the full path
        full_path = os.path.join(directory, entry)
        # Check if the entry is a file and has a .py extension
        if os.path.isfile(full_path) and entry == "__main__.py":
            return True

    return False


def find_main_file():
    dirs = get_dirs()
    for directory in dirs:
        if directory_contains_main(directory):
            return directory

    if directory_contains_main(os.getcwd()):
        return os.getcwd()

    raise Exception("No __main__.py files found")


def load_main_module(directory: str) -> None:
    sys.path.insert(1, directory)
    runpy.run_path("__main__.py", run_name="__main__")


@cli.command()
@click.option("--host", default="127.0.0.1", help="hostname of the webserver")
@click.option("--port", default=8000, help="port to the web server")
def start(host: str, port: int):
    # import __main__ file
    main_file = find_main_file()
    load_main_module(main_file)
    # run server at cli host, port
    run_server(host, port)


@cli.command()
def test():
    # make sure the router is set to testing, so we can also send requests to testing functions
    Router.testing = True

    # import __main__ file
    main_file = find_main_file()
    load_main_module(main_file)

    run_server()
