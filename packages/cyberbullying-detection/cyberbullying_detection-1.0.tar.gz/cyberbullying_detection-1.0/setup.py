from setuptools import setup, find_packages
import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "cyberbullying_detection",
    version = "1.0",
    author = "Omprakash Selvaraj",
    author_email = "omprakash.sr2410@gmail.com",
    description = "An package to detect the cyberbullying content in the text",
    url="https://github.com/omprakashselvaraj/cyberbullying-0.0.1",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages= ['cyberbullying_detection'],
    package_data = {'cyberbullying_detection': ['data/count.pkl','data/lg.pkl']},
    include_package_data = True,
    install_requires = [
        "nltk",
        "num2words",
        "bs4",
        "regex",
        "unidecode"
    ],
    zip_safe = False
)
