"""
A setuptools based setup module.
See:
https://learn.ktechhub.com/tutorials/how-to-package-a-python-code-and-upload-to-pypi/
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import io
from os import path, getenv
from setuptools import setup, find_packages

# Package meta-data.
NAME = "ktechpayapi"
DESCRIPTION = "A python library to consume KtechPay API"
EMAIL = "info@ktechhub.com"
AUTHOR = "KtechHub"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = getenv("VERSION", "0.0.1")  # package version
if "v" in VERSION:
    VERSION = VERSION[1:]

# Which packages are required for this module to be executed?
REQUIRED = [
    "requests",
]

here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with io.open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ktechhub/ktechpay-python",
    # Author details
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    license="MIT",
    keywords="ktechpay python library",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=REQUIRED,
    include_package_data=True,
    setup_requires=["wheel"],
    extras_require={
        "test": ["coverage"],
    },
)
