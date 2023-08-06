import setuptools


with open("requirements.txt") as f:
    requirements = f.read()


setuptools.setup(
    name="hades-cli",
    version="0.0.2",
    author="Wilson Mendoza",
    author_email="mreyeswilson@gmail.com",
    description="A CLI for generating projects",
    url="https://github.com/mreyeswilson/mycli",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hades = app.start:main",
        ]
    },
    include_dirs=["app"],
    python_requires=">=3.8"
)