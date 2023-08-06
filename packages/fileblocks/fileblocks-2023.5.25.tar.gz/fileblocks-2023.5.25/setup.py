from setuptools import setup

from fbi import __version__

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = "fileblocks",
    version = __version__,
    description = "Walk the line, Byte by Byte Analysis",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/jblukach/fbi",
    author = "John Lukach",
    author_email = "hello@lukach.io",
    license = "Apache-2.0",
    packages = ["fbi"],
    install_requires = [
        "blake3",
        "pybloomfiltermmap3",
        "requests",
        "tqdm"
    ],
    entry_points = {
        "console_scripts": [
            "fbi=fbi.cli:main"
        ],
    },
    python_requires = ">=3.7"
)
