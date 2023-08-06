from setuptools import setup, find_packages


VERSION = "0.0.1"
DESCRIPTION = "Python library for shortcuts"

setup(
    name="davipy",
    version=VERSION,
    author="Davide Soltys",
    author_email="<Davide02072003@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pandas", "beautifulsoup4"]
)