# -*- coding: utf-8 -*


import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

    setuptools.setup(
        name="finvader",
        version="1.0.0",
        author="Petr Koráb",
        author_email="xpetrkorab@gmail.com",
        packages=["finvader"],
        description="Python package for exploratory text data analysis",
        long_description=description,
        long_description_content_type="text/markdown",
        url="https://github.com/PetrKorab/FinVADER",
        python_requires='>=3.8',
        install_requires = ['nltk==3.8.1'],
        license='MIT License'
    )