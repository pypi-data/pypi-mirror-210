#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import find_packages, setup


def requirements(path: Path):
    assert path.exists(), "Missing requirements {}".format(path)
    with path.open() as f:
        return list(map(str.strip, f.read().splitlines()))


with open("VERSION") as f:
    VERSION = f.read()

setup(
    name="arkindex-base-worker",
    version=VERSION,
    description="Base Worker to easily build Arkindex ML workflows",
    author="Teklia",
    author_email="contact@teklia.com",
    url="https://teklia.com",
    python_requires=">=3.7",
    install_requires=requirements(Path("requirements.txt")),
    extras_require={"docs": requirements(Path("docs-requirements.txt"))},
    packages=find_packages(),
)
