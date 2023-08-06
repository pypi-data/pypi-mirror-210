import click
from app.handlers.generate.frontend import FrontendGenerator
from app.handlers.generate.backend import BackendGenerator
import os
import pyfiglet

pyfiglet.print_figlet("Hades Toolkit")

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

@click.group()
@click.version_option("0.0.13")
def run():
    """The main entry point of the application"""
    pass


@run.group()
def generate():
    """Generates backend/frontend projects"""
    pass

@generate.command()
def frontend():
    """Generates a frontend project unsing vite"""
    generator = FrontendGenerator()
    generator.run()


@generate.command()
def backend():
    """Generates a backend project"""
    generator = BackendGenerator()
    generator.run()

if __name__ == "__main__":
    run()