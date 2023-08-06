from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()


setup(
    name="hades-cli",
    version="0.0.10",
    packages=find_packages(),
    author="Wilson Mendoza",
    author_email="mreyeswilson@gmail.com",
    description="A CLI for generating projects",
    py_modules=["app"],
    include_dirs=["app"],
    install_requires=[requirements],
    entry_points='''
        [console_scripts]
        hades=app.main:cli
    ''',
)
