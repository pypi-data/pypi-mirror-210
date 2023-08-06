from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'Cleaning Pandas dataframes'
LONG_DESCRIPTION = 'tbd'

# Setting up
setup(
    name="limpo",
    version=VERSION,
    author="Alexander Brück",   
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'data', 'pandas', 'data cleaning', 'data exploration']
)