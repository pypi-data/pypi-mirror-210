#!/usr/bin/env python
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="macrometa-source-bigquery",
    version='0.0.15',
    description="Macrometa source bigquery connector for extracting data from BigQuery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Macrometa",
    url="https://github.com/Macrometacorp/macrometa-source-bigquery",

    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    py_modules=["macrometa_source_bigquery"],
    install_requires=[
        "getschema>=0.1.2",
        "google-cloud-bigquery==3.2.0",
        "simplejson==3.11.1",
        "setuptools>=40.3.0",
        "pipelinewise-singer-python==1.2.0",
        "c8connector>=0.0.20"
    ],

    entry_points="""
    [console_scripts]
    macrometa-source-bigquery=macrometa_source_bigquery:main
    """,

    packages=["macrometa_source_bigquery"],
)
