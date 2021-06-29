import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="redis-tools",
    version="0.0.1",
    author="oiwn",
    author_email="",
    description="Various tools to simplify common use cases for redis in web-scraping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oiwn/redis-tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
