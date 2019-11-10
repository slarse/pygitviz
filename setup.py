import re
import pathlib
from setuptools import setup, find_packages

with open("README.md", mode="r", encoding="utf-8") as f:
    readme = f.read()

# parse the version instead of importing it to avoid dependency-related crashes
with open(pathlib.Path("src")/"_pygitviz"/"__version.py", mode="r", encoding="utf-8") as f:
    line = f.readline()
    __version__ = line.split("=")[1].strip(" '\"\n")
    assert re.match(r"^\d+(\.\d+){2}$", __version__)

test_requirements = ["pytest>=4.0.0", "pytest-cov>=2.6.0", "pytest-mock", "codecov"]
required = ["daiquiri"]

setup(
    name="pygitviz",
    version=__version__,
    description="Git repository visualizer for demonstrational and educational purposes",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simon Larsén",
    author_email="slarse@kth.se",
    url="https://github.com/slarse/pygitviz",
    download_url=(
        "https://github.com/slarse/pygitviz/archive/v{}.tar.gz".format(__version__)
    ),
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(exclude=("tests", "docs")),
    tests_require=test_requirements,
    install_requires=required,
    extras_require=dict(TEST=test_requirements),
    include_package_data=True,
    zip_safe=False,
    scripts=["bin/pygitviz"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows :: Windows 10",
    ],
    python_requires=">=3.6",
)
