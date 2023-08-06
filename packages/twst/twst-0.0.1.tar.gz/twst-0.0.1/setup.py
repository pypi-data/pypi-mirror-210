from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'write text in a typewriter style similar to the print() function'
LONG_DESCRIPTION = 'A python package for writing text in a typewriter style similar to the print() function.'

# Setting up
setup(
    name="twst",
    version=VERSION,
    author="gdsonicpython",
    author_email="<hatenal.official@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["time", "sys"],
    keywords=['python', 'print', 'typewriter'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)