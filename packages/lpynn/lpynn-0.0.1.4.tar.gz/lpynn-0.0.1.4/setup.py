# The setup.py file is used as the build script for setuptools. Setuptools is a
# package that allows you to easily build and distribute Python distributions.

import setuptools

# Define required packages. Alternatively, these could be defined in a separate
# file and read in here.
REQUIRED_PACKAGES=["lpython_emulation"]

VERSION="0.0.1.4"

# Read in the project description. We define this in the README file.
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lpynn",                                               # name of project
    install_requires=REQUIRED_PACKAGES,                         # all requirements used by this package
    version=VERSION,                                            # project version, read from version.py
    author="Ubaid Shaikh",                                      # Author, shown on PyPI
    author_email="shaikhubaid769@gmail.com",                    # Author email
    description="A basic neural networks python package",       # Short description of project
    long_description=long_description,                          # Long description, shown on PyPI
    long_description_content_type="text/markdown",              # Content type. Here, we used a markdown file.
    url="https://github.com/Shaikh-Ubaid/lpython_packages",     # github path
    packages=setuptools.find_packages(),                        # automatically finds packages in the current directory. You can also explictly list them.
    classifiers=[                                               # Classifiers give pip metadata about your project. See https://pypi.org/classifiers/ for a list of available classifiers.
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',                                    # python version requirement
)
