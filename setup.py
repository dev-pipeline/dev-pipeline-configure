#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="dev-pipeline-configure",
    version="0.2.0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    install_requires=[
        'dev-pipeline-core >= 0.2.0'
    ],

    entry_points={
        'devpipeline.drivers': [
            'configure = devpipeline_configure.configure:main'
        ]
    },

    author="Stephen Newell",
    description="configure command for dev-pipeline",
    license="BSD-2"
)
