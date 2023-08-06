from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Machine Learning Network(MLNet).'
LONG_DESCRIPTION = 'A package to perform and manage the machine learning algoriths structure.'

# Setting up
setup(
    name="MLNets",
    version=VERSION,
    author="Suriya Vijay",
    author_email="suriyavijay@mail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['mlnets', 'MLnets', 'MLNets', 'machine learning networks', 'MLNETS'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)