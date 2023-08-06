from setuptools import setup, find_packages

# read the contents of README file
from pathlib import Path
this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

VERSION = '2.0.2'
DESCRIPTION = 'REFRACT-IO: To read and write dataframe from different connectors.'

extras_require = {
    "all": [
        "snowflake-connector-python[pandas]==3.0.2",
        "boto3==1.26.116",
        "azure==4.0.0",
        "openpyxl==3.1.2",
        "xlrd==2.0.1",
        "pysftp==0.2.9",
        "pymysql==1.0.3",
        "impyla==0.16.2",
        "thrift-sasl==0.4.3",
        "pure-sasl==0.6.2",
        "PyHive==0.6.3.dev0"
    ],
    "snowflake": [
        "snowflake-connector-python[pandas]==3.0.2"
    ],
    "s3": [
        "boto3==1.26.116"
    ],
    "azureblob": [
        "azure==4.0.0"
    ],
    "local": [
        "openpyxl==3.1.2",
        "xlrd==2.0.1",
    ],
    "sftp": [
        "pysftp==0.2.9"
    ],
    "mysql": [
        "pymysql==1.0.3"
    ],
    "hive": [
        "impyla==0.16.2",
        "thrift-sasl==0.4.3",
        "pure-sasl==0.6.2",
        "PyHive==0.6.3.dev0"
    ]
}

# Setting up
setup(
    name="refractio",
    version=VERSION,
    author="Abhishek Chaurasia",
    author_email="<abhishek1.chaurasia@fosfor.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas==2.0.0"
    ],
    keywords=['refractio'],
    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],
    extras_require=extras_require,
    project_urls={
        "Product": "https://www.fosfor.com/refract/",
        "Source": "https://git.lti-aiq.in/refract-sdk/refract-sdk",
    }
)
