#!/usr/bin/env python3

import os
from typing import Union, Any

from setuptools import setup

import seqslab

setup_file_loc: Union[Union[str, bytes], Any] = os.path.abspath(
    os.path.dirname(__file__))
# allow setup.py to be run from any path
os.chdir(setup_file_loc)

extras_require = {}


def get_requirement():
    requirements = [  # dependency list
        'pip>=22.0.4'
    ]
    with open(os.path.join(setup_file_loc, 'requirements.txt'), 'r') as f:
        ori_req = f.read().splitlines()
    requirements.extend(ori_req)
    return requirements


def readme():
    path = os.path.join(setup_file_loc, 'README.md')
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


setup(
    name="seqslab-connector",
    version=seqslab.__version__,
    description="Atgenomix SeqsLab Connector for Python",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/atgenomix/seqslab-connector",
    author="Allen Chang",
    author_email="allen.chang@atgenomix.com",
    license="Apache License, Version 2.0",
    packages=["seqslab", "seqslab.sqlalchemy", "seqslab.superset"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    data_files=[('requirements', ['requirements.txt'])],
    install_requires=get_requirement(),
    extras_require={
        "sqlalchemy": ["sqlalchemy>=1.3.0"],
        "superset": ["superset>=2.0.1"],
    },
    tests_require=[],
    cmdclass={},
    package_data={
        "": ["*.rst"],
    },
    entry_points={
        "sqlalchemy.dialects": [
            "seqslab.hive = seqslab.sqlalchemy.hive:SeqsLabHiveDialect",
        ],
        "superset.db_engine_specs": [
            "seqslab = seqslab.superset.seqslab:SeqsLabHiveEngineSpec",
        ],
    }
)
