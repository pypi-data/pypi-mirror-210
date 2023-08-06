from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="remla12-lib-release",
    version="0.0.2",
    description="A version-aware library for REMLA12 project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/remla23-team12/lib",
    packages=find_packages(),
    python_requires=">=3.6",
)
