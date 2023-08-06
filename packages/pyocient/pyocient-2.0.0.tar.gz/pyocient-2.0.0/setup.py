"""Ocient Database Python API
"""

import os
import pathlib
from typing import Dict

from setuptools import setup

here = pathlib.Path(__file__).parent.absolute()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

with open(os.path.join(here, "pyocient", "pkg_version.py")) as version_file:
    globals: Dict[str, str] = {}
    exec(version_file.read(), globals)
    version = globals["__version__"]

setup(
    name="pyocient",
    version=version,
    description="Ocient Database Python API",
    author="Ocient Inc",
    author_email="info@ocient.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.ocient.com/",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Typing :: Typed",
    ],
    keywords="database, sql, development",
    setup_requires=[
        "wheel",
    ],
    install_requires=[
        "dsnparse<=0.1.15",
        "prompt-toolkit",
        "pygments",
        "tabulate",
        "cryptography",
        "protobuf>=3.20.0,<=4.22.0",
    ],
    packages=["pyocient"],
    package_data={"pyocient": ["py.typed"]},
    entry_points={
        "console_scripts": [
            "pyocient=pyocient.cli:main",
        ],
    },
    python_requires=">=3.7, <4",
    options={"bdist_wheel": {"universal": "1"}},
)
