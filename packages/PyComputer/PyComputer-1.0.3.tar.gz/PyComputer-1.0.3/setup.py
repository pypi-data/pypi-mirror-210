# PyComputer - Setup.py

''' This is the 'setup.py' file. '''

# Imports
from setuptools import setup, find_packages

# README.md
with open("README.md") as readme_file:
    README = readme_file.read()

# Setup Arguements
setup_args = dict (
    name="PyComputer",
    version="1.0.3",
    description="PyComputer is an advanced Python package that manages and alters your computer's settings.",
    long_description_content_type="text/markdown",
    long_description=README,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    author="Aniketh Chavare",
    author_email="anikethchavare@outlook.com",
    keywords=["Computer", "Settings"],
    url="https://github.com/Anikethc/PyComputer",
    download_url="https://pypi.org/project/PyComputer"
)

# Classifiers
classifiers = [
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python"
]

# Install Requires
install_requires = ["screen-brightness-control"]

# Run the Setup File
if __name__ == "__main__":
    setup(**setup_args, install_requires=install_requires, classifiers=classifiers)