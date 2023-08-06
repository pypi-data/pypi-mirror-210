#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import glob

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest>=3",
]
# ["*.op2", "*.OP2", "*.ini", "*.nas", "*.dat", "*.bdf", "*.j2", "*.css"],
data_files = glob.glob("mystran_validation/data/**/*.op2", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.OP2", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.ini", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.nas", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.dat", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.bdf", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.j2", recursive=True)
data_files += glob.glob("mystran_validation/data/**/*.css", recursive=True)

setup(
    author="Nicolas Cordier",
    author_email="nicolas.cordier@numeric-gmbh.ch",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python framework for MYSTRAN validation",
    entry_points={
        "console_scripts": [
            "mystran-val=mystran_validation.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="mystran_validation",
    name="mystran_validation",
    packages=find_packages(include=["mystran_validation", "mystran_validation.*"]),
    data_files=[
        ("mystran_validation/data", data_files),
    ],
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    version="0.16.0",
    zip_safe=False,
)
