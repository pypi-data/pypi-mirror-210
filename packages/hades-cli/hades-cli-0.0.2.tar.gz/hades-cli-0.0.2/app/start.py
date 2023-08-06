import click
from app.handlers.generate.frontend import FrontendGenerator
from app.handlers.generate.backend import BackendGenerator
import os
import pyfiglet

pyfiglet.print_figlet("Hera Toolkit")

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

@click.group()
def main():
    """The main entry point of the application"""
    pass


@main.group()
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