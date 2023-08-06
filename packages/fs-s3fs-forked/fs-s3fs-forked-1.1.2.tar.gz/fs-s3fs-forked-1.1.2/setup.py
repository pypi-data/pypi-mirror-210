#!/usr/bin/env python

from setuptools import setup, find_packages

with open("fs_s3fs/_version.py") as f:
    exec(f.read())

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Topic :: System :: Filesystems",
]

with open("README.rst", "rt") as f:
    DESCRIPTION = f.read()

REQUIREMENTS = ["boto3~=1.9", "fs~=2.4", "six~=1.10"]

setup(
    name="fs-s3fs-forked",
    author="Antoine Desbordes",
    author_email="antoine.desbordes@gmail.com",
    classifiers=CLASSIFIERS,
    description="Amazon S3 filesystem for PyFilesystem2, forked from https://github.com/PyFilesystem/s3fs",
    install_requires=REQUIREMENTS,
    license="MIT",
    long_description=DESCRIPTION,
    packages=find_packages(),
    keywords=["pyfilesystem", "Amazon", "s3"],
    platforms=["any"],
    test_suite="nose.collector",
    url="https://gitlab.com/geovisio/infra/s3fs",
    version=__version__,
    entry_points={"fs.opener": ["s3 = fs_s3fs.opener:S3FSOpener"]},
)
