#!/usr/bin/env python3

from setuptools import setup

setup(
    name="wisdomweaver",
    version="2.1",
    description="Language model based wisdom generator.",
    long_description=open("README.md").read(),
    license="GPLv3",
    packages=["wisdomweaver"],
    scripts=["wisdom"],
    # package_data={"wisdomweaver": ["data/*"]},
)
