from setuptools import setup, find_packages
import os
from pathlib import Path

here = Path(os.path.dirname(os.path.abspath(__file__)))

main_ns = {}
with (here / "dash_labs" / "version.py").open() as f:
    exec(f.read(), main_ns)  # pylint: disable=exec-used


def requirements_txt():
    with open(here / 'requirements.txt', 'rt') as f:
        return [line.strip() for line in f.read().split("\n")]


setup(
    name="dash-labs",
    version=main_ns["__version__"],
    python_requires=">=3.6.*",
    packages=find_packages(),
    install_requires=requirements_txt(),
)
