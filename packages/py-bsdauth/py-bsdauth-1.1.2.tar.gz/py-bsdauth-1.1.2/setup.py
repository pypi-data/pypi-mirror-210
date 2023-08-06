import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="py-bsdauth",
    version="1.1.2",
    description="Python interface to OpenBSD's BSD Auth.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rbaylon/py-bsdauth",
    author="Ricardo Baylon",
    author_email="rbaylon@outlook.com",
    license="ISC",
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3"
    ],
    packages=["bsdauth"],
    include_package_data=True,
    platforms=["OpenBSD"]
)
