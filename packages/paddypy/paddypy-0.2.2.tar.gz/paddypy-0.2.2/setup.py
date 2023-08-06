from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2.2'
DESCRIPTION = 'Collection of helpfull extensions'
LONG_DESCRIPTION = 'Collection of helpfull extensions'

# Setting up
setup(
    name="paddypy",
    version=VERSION,
    author="Patrik",
    author_email="<patrikhartl@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['azure-appconfiguration>=1.1.1', 'texttable>=1.4.4', 'azure-identity>=1.5.0', 'azure-keyvault-secrets>=4.1.0', 'opencensus-ext-azure>=1.1.9'],
    keywords=['python', 'appconfiguration', 'azure'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Environment :: Web Environment"
    ]
)