# Always prefer setuptools over distutils
from setuptools import setup

# This call to setup() does all the work
setup(
    name="serializer_ByKaxxa",
    version="0.1.0",
    description="JSON / XML serializer",
    author="Kakhnouski Eugene",
    author_email="Kaxxa2927@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ],
    packages=["serializer", "serializer_factory", "json_serializer", "xml_serializer"],
    include_package_data=True,
    install_requires=["regex"]
)
