import os
from setuptools import setup, find_packages


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="yolo-pyutils",
    version="0.1.34",
    author="Tao Yang",
    author_email="ytaofighting@gmail.com",
    description="yolo-pyutils provides utility functions for IO, data-processing, scheduling, common structures etc.",
    license="Apache License 2.0",
    keywords="utils",
    url="https://github.com/TaoYang526/yolo-pyutils",
    packages=find_packages(),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        'License :: OSI Approved :: Apache Software License',
        "Programming Language :: Python :: 3"
    ],
)
