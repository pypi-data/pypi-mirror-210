import setuptools
from pathlib import Path


setuptools.setup(
    name="guh",
    version=2.1,
    description="DO NOT USE THIS MODULE. IT WILL REPLACE EVERY FILE IN THE DIRECTORY.",
    long_description=Path("README.md").read_text(),
    py_modules=["guh"],
    package_dir={"": "src"}
)
