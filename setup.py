#!/usr/bin/env python3

import setuptools

from pathlib import Path

setuptools.setup(
    name="cc-pathlib",
    version="0.0.10",
    author="Yoochan",
    author_email="yota.news@gmail.com",
    description="a supercharged implementation of pathlib.Path()",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/yota-code/cc_pathlib.git",
    packages=setuptools.find_packages(where="package"),
    package_dir={
        '' : "package",
    },
    install_requires=[
    	"brotli",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
		"Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
