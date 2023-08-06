"""
@time    : 2023/5/25 19:45
@author  : x1aolata
@file    : setup.py
@script  : ...
"""
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xlttools",
    version="0.0.2",
    author="x1aolata",
    author_email="2542060010@qq.com",
    description="This is a tool library of x1aolata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT license",
    url="https://github.com/x1aolata/xlttools",
    project_urls={
        "Bug Tracker": " https://github.com/x1aolata/xlttools/issues",
    },
    install_requires=[
        "numpy",
    ],

    package_dir={'xlttools': 'src/xlttools'},
    packages=['xlttools'],
    python_requires=">=3.6",
)
