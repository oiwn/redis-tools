# pylint: disable=missing-module-docstring
import sys
import setuptools  # type: ignore


if sys.version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="redis-tools",
    version="0.0.6",
    author="oiwn",
    author_email="",
    description=(
        "Various tools to simplify common use-cases for redis in web-scraping"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oiwn/redis-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
