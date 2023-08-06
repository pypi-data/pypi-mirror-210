from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Instagram Android Api For Login '
LONG_DESCRIPTION = 'A python library that helps you to login in instagram do various task and automaiton'

# Setting up
setup(
    name="gamerinsta",
    version=VERSION,
    author="Gamer",
    author_email="godxgamer0192@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['httpx','user_agent','uuid','requests',],
    keywords=['Instagram','login'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)