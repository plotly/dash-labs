from setuptools import setup, find_packages
import os
from pathlib import Path

here = Path(os.path.dirname(os.path.abspath(__file__)))

main_ns = {}
with (here / "dash_labs" / "version.py").open() as f:
    exec(f.read(), main_ns)  # pylint: disable=exec-used


def requirements_txt():
    with open(here / "requirements.txt", "rt") as f:
        return [line.strip() for line in f.read().split("\n")]


def readme():
    with open(here / "README.md", "rt") as f:
        return f.read()


setup(
    name="dash-labs",
    version=main_ns["__version__"],
    author="Chris Parmer",
    author_email="chris@plot.ly",
    maintainer="Chris Parmer",
    maintainer_email="chris@plot.ly",
    url="https://github.com/plotly/dash-labs",
    project_urls={"Github": "https://github.com/plotly/dash-labs"},
    description="Experimental enhancements for potential inclusion in Dash",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Visualization",
        "Framework :: Dash",
    ],
    license="MIT",
    license_files=["LICENSE.txt"],
    python_requires=">=3.6.*",
    packages=find_packages(exclude=["tests", "tests.*"]),
)
