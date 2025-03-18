from setuptools import setup, find_packages

setup(
    name="shared",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "SQLAlchemy==2.0.38",
        "pydantic==2.10.6",
        "redis==5.2.1",
    ],
)
