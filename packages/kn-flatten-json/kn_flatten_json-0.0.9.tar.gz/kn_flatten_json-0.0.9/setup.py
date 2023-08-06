from setuptools import setup, find_packages
import codecs
import os
from pathlib import Path
this_directory = Path(__file__).parent
VERSION = '0.0.9'
DESCRIPTION = 'kn_flatten_json'
LONG_DESCRIPTION = (this_directory / "README.md").read_text()


# Setting up
setup(
    name="kn_flatten_json",
    version=VERSION,
    author="Sukriti",
    author_email="sukriti.saluja@kockpit.in",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['flatten', 'json', 'normalize', 'normalize pyspark dataframe', 'complex datatypes', 'flatten dataframe'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
