import setuptools
from pathlib import Path

setuptools.setup(
    name="PLpy234 project 1",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
