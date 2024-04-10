from .routing.router import Router
from .webwithpy import run_server
from pydoc import importfile
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
            return directory + "/__main__.py"

    if directory_contains_main(os.getcwd()):
        return os.getcwd() + "/__main__.py"

    raise Exception("No __main__.py files found")


@cli.command()
@click.option("--host", default="127.0.0.1", help="hostname of the webserver")
@click.option("--port", default=8000, help="port to the web server")
def start(host: str, port: int):
    # import __main__ file
    main_file = find_main_file()
    importfile(main_file)

    # run server at cli host, port
    run_server(host, port)


@cli.command()
def test():
    # make sure the router is set to testing, so we can also send requests to testing functions
    Router.testing = True

    # import __main__ file
    main_file = find_main_file()
    importfile(main_file)

    run_server()
