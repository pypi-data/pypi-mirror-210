from setuptools import setup, find_packages


with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()


setup(
    name="hades-cli",
    version="0.0.5.2",
    packages=find_packages(),
    author="Wilson Mendoza",
    author_email="mreyeswilson@gmail.com",
    description="A CLI for generating projects",
    py_modules=["app"],
    include_dirs=["app"],
    install_requires=[requirements],
    entry_points='''
        [console_scripts]
        hades=app.application:cli
    ''',
)               