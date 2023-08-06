from setuptools import setup

from pymorlocinternals.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pymorlocinternals",
    version=__version__,
    description="Python serialization code for morloc interoperability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/morloc-project/pymorlocinternals",
    author="Zebulun Arendsee",
    author_email="zbwrnz@gmail.com",
    packages=["pymorlocinternals"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["pymorlocinternals"],
    zip_safe=False,
)
