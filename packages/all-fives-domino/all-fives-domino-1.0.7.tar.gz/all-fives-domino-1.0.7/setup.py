from setuptools import setup, find_packages

print(f"SETUP: {__file__}")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("version.txt", "r", encoding="utf-8") as fh:
    VERSION = fh.read()

NAME = "all-fives-domino"
DESCRIPTION = "Abstractions around cloud file interfaces (WIP)"
URL = "https://github.com/Informanthik/all-fives-domino"
EMAIL = "jakob-hoefner@web.de"
AUTHOR = "Jothapunkt"
REQUIRED = [

]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    install_requires=REQUIRED,
    url=URL,
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    include_package_data=True
)
