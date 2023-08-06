from setuptools import setup, find_packages

VERSION = '0.2.6'
DESCRIPTION = 'Simplifies writing MySQL statements in non-ORM environments.'

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='mysql-statement-builder',
    version=VERSION,
    description=DESCRIPTION,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[],
    extras_require={
        "dev": [
            "pytest==7.*",
            "twine>=4.0"
        ]
    },
    url="https://github.com/johnmartins/mysql-statement-builder",
    author="Julian Martinsson Bonde",
    author_email="julianm@chalmers.se"
)
