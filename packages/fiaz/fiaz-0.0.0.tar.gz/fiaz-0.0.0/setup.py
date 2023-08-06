from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.0'
DESCRIPTION = 'Fiaz is a Python package in Active Development that aims to provide various AI capabilities, ' \
              'including a chatbot, image processing, audio processing, Django & flask support, and more.'
LONG_DESCRIPTION = 'NOTE: This package is currently under development and not yet ready for production use. Use it at ' \
                   'your own risk. Fiaz is a Python package in Active Development that aims to provide various AI ' \
                   'capabilities, including a chatbot, image processing, audio processing, Django & flask support, ' \
                   'and more. It utilizes TensorFlow and other related technologies for natural language processing ' \
                   'and AI tasks.'

# Setting up
setup(
    name="fiaz",
    version=VERSION,
    author="Muhammad Fiaz",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['fiaz', 'muhammad fiaz'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)