import setuptools
from pathlib import Path


setuptools.setup(
    name="guh",
    version=2.0,
    long_description=Path("README.md").read_text(),
    py_modules=["guh"],
    package_dir={"": "src"}
)
