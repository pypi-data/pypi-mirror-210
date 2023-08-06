from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

setup(
    name="hades-cli",
    version="0.0.12",
    packages=find_packages(),
    author="Wilson Mendoza",
    author_email="mreyeswilson@gmail.com",
    description="A CLI for generating projects",
    include_dirs=["app"],
    install_requires=[requirements],
    entry_points='''
        [console_scripts]
        hades=app.main:run
    ''',
)
