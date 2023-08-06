#!/usr/bin/env python3

import pathlib

import setuptools

CWD = pathlib.Path(__file__).parent

README = (CWD / "README.md").read_text()

LICENSE = (CWD / "LICENSE").read_text()

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='p10k-edit',
    version='0.0.4',
    author='Teddy Katayama',
    author_email='katayama@udel.edu',
    description='Tool to Edit PowerLevel10k p10k.zsh Config File (work-in-progress)',
    license = LICENSE,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kkatayama/p10k-edit',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'p10k-edit=p10k_edit.bin.__main__:main'
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
