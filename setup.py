from setuptools import setup, find_packages
import os
from pathlib import Path

here = Path(os.path.dirname(os.path.abspath(__file__)))


def requirements_txt():
    with open(here / 'requirements.txt', 'rt') as f:
        return [line.strip() for line in f.read().split("\n")]


setup(
    name="dash-labs",
    packages=find_packages(),
    install_requires=requirements_txt(),
)
