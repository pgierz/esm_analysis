#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["cdo", "Click>=6.0", "pandas", "tabulate", "regex-engine", "pyyaml"]

setup_requirements = []

test_requirements = []

# Unpublished packages not on PyPI (e.g pyfesom)
dependency_links = [
    "https://github.com/FESOM/pyfesom/tarball/master"
]  # , 'http://github.com/user/repo/tarball/master#egg=package-1.0']

setup(
    author="Paul Gierz",
    author_email="pgierz@awi.de",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Analysis Scripts for ESM Simulations",
    entry_points={"console_scripts": ["esm_analysis=esm_analysis.cli:main"]},
    install_requires=requirements,
    dependency_links=dependency_links,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="esm_analysis",
    name="esm_analysis",
    packages=find_packages(),
    # packages=find_packages(include=["esm_analysis"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/pgierz/esm_analysis",
    version="0.4.2",
    zip_safe=False,
)
