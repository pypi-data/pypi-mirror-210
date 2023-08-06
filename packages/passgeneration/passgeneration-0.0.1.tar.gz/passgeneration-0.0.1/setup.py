from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='passgeneration',
    version='0.0.1',
    description='Password Generating Library. Fixed Name Version',
    author='aroko900',
    author_email='aro0ko1@xmailer.be',
    license='MIT',
    keywords = ['password generator', 'password'],
    packages=["passgeneration"],
    url="https://github.com/Aroko001/PassGeneration-py",
    include_package_data=True,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License"
    ]
)