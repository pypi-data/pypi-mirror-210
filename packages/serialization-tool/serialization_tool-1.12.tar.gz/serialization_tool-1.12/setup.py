from setuptools import setup, find_packages


setup(
    name="serialization_tool",
    version="1.12",
    license="GNU GENERAL PUBLIC LICENSE",
    author="Alexander Skvortsov",
    author_email="alexskvr03@gmail.com",
    packages=find_packages("src"),
    package_dir={'':'src'},
    url="https://github.com/ALFecki/python-labs/tree/lab-3/lab-3/serialization_tool",
    keywords="serialization xml json",

)
