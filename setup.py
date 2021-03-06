"""
Setup module for pygaiav1.

Anthony Brown 2012--2019

Based on:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

from codecs import open
from os import path
import re

this_folder = path.abspath(path.dirname(__file__))

# Get the long description from the README and HISTORY files
with open(path.join(this_folder, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
with open(path.join(this_folder, 'HISTORY.rst'), encoding='utf-8') as f:
    history = f.read()

# Get code version from __init__.py (see https://github.com/dfm/emcee/blob/master/setup.py)
vre = re.compile("__version__ = \"(.*?)\"")
m = open(path.join(this_folder, "pygaiav1", "__init__.py")).read()
codeVersion = vre.findall(m)[0]

setup(
        name='pygaiav1',

        version=codeVersion,

        description='Basic Gaia data simulation, manipulation, and analysis toolkit',
        long_description=long_description + "\n\n"
        + 'Changelog\n'
        + '---------\n\n'
        + history,

        url='https://github.com/agabrown/pygaia-v1',

        author='Anthony Brown',
        author_email='brown@strw.leidenuniv.nl',

        license='LGPLv3+',

        #packages=['pygaiav1', 'pygaiav1.errors', 'pygaiav1.astrometry', 'pygaiav1.photometry', 'pygaiav1.plot',
        #  'pygaiav1.tests'],
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        package_data={'': ['LICENSE', 'AUTHORS.rst', 'HISTORY.rst', 'INSTALL', 'MANIFEST.in'],
            'pygaiav1': ['data/*.txt']},
        include_package_data=True,
        install_requires=[ 'numpy', 'scipy' ],

        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Topic :: Scientific/Engineering :: Astronomy',
            ],

        entry_points={},
        )
