# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))


# This call to setup() does all the work
setup(
    name="geodistance",
    version="0.1.6",
    description="Distance calculation library",
    long_description="A library that is used to calculate the distance between 2 coordinates \ **Installation** \ `pip install geodistance` \ **Get Started** \ Calculating distance between 2 coordinates \ `from geodistance import Geodistance` \ `length = Geodistance().distance(42.546245, 1.601554, 23.424076, 53.847818)` \ `print(length)`",
    long_description_content_type="text/markdown",
    url="https://geodistance.readthedocs.io/",
    author="Adebayo Adeoye",
    author_email="adeoyeadebayo18@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["geodistance"],
    include_package_data=True,
    install_requires=[]
)