# This file is placed in the Public Domain.


from setuptools import setup


def read():
    return open("README.rst", "r").read()


setup(
    name="opd",
    version="100",
    author="No Paths <nopaths@proton.me>",
    author_email="nopaths@proton.me",
    url="http://github.com/nopaths/opd",
    zip_safe=True,
    description="operator daemon",
    long_description=read(),
    long_description_content_type="text/x-rst",
    license="Public Domain",
    packages=[
              "opd",
              'opd.modules'
             ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: Public Domain",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
     ],
)
