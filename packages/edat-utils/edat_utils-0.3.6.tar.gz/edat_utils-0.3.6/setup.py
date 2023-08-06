# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="edat_utils",
    version="0.3.6",
    description="Biblioteca de Apoio ao desenvolvimento no EDAT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Escritório de Dados",
    author_email="dados@unicamp.br",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ],
    packages=["edat_utils"],
    include_package_data=True,
    install_requires=["trino", "SQLAlchemy", "python-decouple", "strawberry-graphql"]
)