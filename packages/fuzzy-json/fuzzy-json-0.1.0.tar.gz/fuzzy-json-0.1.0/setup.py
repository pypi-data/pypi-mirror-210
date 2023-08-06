from os import path

from setuptools import setup
from setuptools_rust import RustExtension

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="fuzzy-json",
    version="0.1.0",
    author="cympfh",
    author_email="cympfh@gmail.com",
    url="https://github.com/cympfh/fuzzy-json-py",
    description="Python Binding for Fuzzy JSON Parser (fson)",
    classifiers=["License :: OSI Approved :: MIT License"],
    long_description=long_description,
    packages=["fuzzy_json"],
    rust_extensions=[RustExtension("fuzzy_json.fuzzy_json", "Cargo.toml", debug=False)],
    include_package_data=True,
    zip_safe=False,
)
