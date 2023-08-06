from setuptools import setup

setup(
    name="alkira-sdk",
    version="1.0.1",
    description="A Python SDK for interacting with Alkira",
    author="Hemat Kumar <hemant4.kumar@orange.com>",
    packages=["alkira"],
    install_requires=[
        "requests"
    ],
)
