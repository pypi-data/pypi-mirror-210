from setuptools import setup, find_packages
import logging

logger = logging.getLogger(__name__)

version = "0.0.5"

try:
    with open("README.md", "r") as f:
        long_desc = f.read()
except:
    logger.warning("Could not open README.md.  long_description will be set to None.")
    long_desc = None

setup(
    name="grid2fp",
    packages=find_packages(),
    version=version,
    description="A tool to eat grid diagrams and generate its front projection.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="Casey Duckering",
    # author_email = '',
    url="https://github.com/Joecstarr/grid2fp",
    keywords=["topology", "Legendrian", "Grid Diagram","knot"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Framework :: IPython",
    ],
    python_requires='>=3',
    install_requires=["drawsvg",]
)
