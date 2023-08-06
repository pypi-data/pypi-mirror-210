# PyEng - Setup.py

''' This is the 'setup.py' file. '''

# Imports
from setuptools import setup, find_packages

# README.md
with open("README.md") as readme_file:
    README = readme_file.read()

# Setup Arguements
setup_args = dict (
    name="PyEng",
    version="1.0.4",
    description="PyEng is a general-purpose Python package that contains functions related to the English language.",
    long_description_content_type="text/markdown",
    long_description=README,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    author="Aniketh Chavare",
    author_email="anikethchavare@outlook.com",
    keywords=["English"],
    url="https://github.com/Anikethc/PyEng",
    download_url="https://pypi.org/project/PyEng"
)

# Run the Setup File
if __name__ == "__main__":
    setup(**setup_args)