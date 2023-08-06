from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name = "test-jack-py",
    version = "0.0.1",
    description = "this is test python package",
    packages = ['test-jack'],
    py_modules = ["out-module"],
    author = "jack",
    author_email = "1039990656@qq.com",
    long_description = long_description,
    license = "MIT"
)
