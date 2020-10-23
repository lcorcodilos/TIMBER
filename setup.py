import setuptools, subprocess, os

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="TIMBER", # Replace with your own username
    version="0.2",
    author="lcorcodilos",
    author_email="corcodilos.lucas@gmail.com",
    description="Tree Interface for Making Binned Events with RDataFrame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lcorcodilos/TIMBER",
    packages=setuptools.find_packages(),
    include_package_data=True,
    # cmdclass={'install': AddToPath},
    install_requires = [
        "pygraphviz",
        "networkx",
        "clang==6.0.0.2"
    ]
)

