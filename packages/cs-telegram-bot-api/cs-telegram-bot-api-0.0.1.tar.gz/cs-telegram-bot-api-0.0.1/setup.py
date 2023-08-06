from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Telegram Bot API Wrapper'
LONG_DESCRIPTION = 'A Python module for interacting with the Telegram Bot API.'

# Setting up
setup(
    name="cs-telegram-bot-api",
    version=VERSION,
    author="Richard",
    author_email="<rich_swainson@hotmail.co.uk>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['telegram', 'bot', 'api', 'wrapper'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
