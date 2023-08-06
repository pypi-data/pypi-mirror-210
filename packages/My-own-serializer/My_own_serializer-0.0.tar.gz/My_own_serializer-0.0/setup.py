from setuptools import setup

setup(
    name="My_own_serializer",
    version="0.0",
    description="Library for converting objects to xml and json format",
    url="https://github.com/andrw04/Python-labs/tree/lab3",
    author="Andrei Sivy",
    author_email="sivyandrey2021@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
    packages=["serializer"],
    include_package_data=True,
    install_requires=["regex"]
)