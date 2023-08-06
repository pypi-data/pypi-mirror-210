from setuptools import setup, find_packages

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name="logfrog",
    version="1.0.0",
    author="Lakshya Gupta",
    description="A simple and efficient logging package in python with async support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fuushyn/logfrog",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
