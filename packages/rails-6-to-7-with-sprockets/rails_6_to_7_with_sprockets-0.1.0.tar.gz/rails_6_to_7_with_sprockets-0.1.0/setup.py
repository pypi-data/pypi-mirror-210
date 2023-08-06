#!/usr/bin/env python

from setuptools import find_packages
from setuptools import setup

setup(
    name='rails_6_to_7_with_sprockets',
    version="0.1.0",
    description='Update rails 6 to 7 with sprockets',
    author='Angel Garcia',
    author_email='angarc37@gmail.com',
    url='https://github.com/angarc/rails_6_to_7_with_sprockets',
    py_modules=[
        'rails_6_to_7_with_sprockets.__main__',
    ],
    packages=find_packages(),
    # install_requires=[
    # ],
    entry_points={'console_scripts': ['r6t7 = rails_6_to_7_with_sprockets.__main__:main']},
)