from setuptools import setup
from pycliwrapper import __version__


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='pycliwrapper',
    version=__version__,
    author='Jordi Deu-Pons',
    description='Wrap any CLI tool to Python like syntax',
    long_description=readme(),
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
    keywords=["cli", "wrapper"],
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers"
    ]
)