# Copyright (c) 2016 Florian Wagner
#
# This file is part of pyAffy.
#
# pyAffy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import io

from setuptools import setup, find_packages, Command, Extension
#from os import path

here = os.path.abspath(os.path.dirname(__file__))

name = 'pyaffy'
root = 'pyaffy'
version = '0.3.2'

description = (
    'pyAffy: Processing raw data from Affymetrix expression microarrays in Python.'
)

# get long description from file
long_description = ''
with io.open(os.path.join(here, 'README.rst'),
        mode = 'r', encoding = 'utf-8') as fh:
    long_description = fh.read()

ext_modules = []
cmdclass = {}

try:
    # this can fail if numpy or cython isn't installed yet
    import numpy as np
    from Cython.Distutils import build_ext
    from Cython.Compiler import Options as CythonOptions

except ImportError:
    pass

else:
    ### Specify Cython modules

    ext_modules.append(
        Extension(
            root + '.' + 'celparser',
            sources= [root + os.sep + 'celparser.pyx'],
            include_dirs = [np.get_include()],
        )
    )

    ext_modules.append(
        Extension(
            root + '.' + 'cdfparser',
            sources= [root + os.sep + 'cdfparser.pyx'],
            include_dirs = [np.get_include()],
        )
    )

    ext_modules.append(
        Extension(
            root + '.' + 'medpolish',
            sources= [root + os.sep + 'medpolish.pyx'],
            include_dirs = [np.get_include()],
        )
    )

    cmdclass['build_ext'] = build_ext

class CleanCommand(Command):
    """Removes files generated by setuptools.

    """
    # see https://github.com/trigger/trigger/blob/develop/setup.py
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        error_msg = 'You must run this command in the package root!'
        assert os.getcwd() == here, error_msg
        os.system ('rm -rf ./dist ./build ./*.egg-info ')

cmdclass['clean'] = CleanCommand

setup(

    name = name,

    version = version,

    description = description,

    long_description = long_description,

    author = 'Florian Wagner',
    author_email = 'florian.wagner@duke.edu',
    license = 'GPLv3',

    # homepage
    url = 'https://github.com/flo-compbio/pyaffy',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 2.7',
    ],

    keywords = 'affymetrix microarray rma expression normalization',

    #packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    packages = find_packages(exclude = ['docs']),

	#libraries = [],

    #install_requires = ['unicodecsv', 'xmltodict'],
    install_requires = [
        'six>=1.10.0, <2',
        # 'future>=0.16, <1',
        'python-dateutil>=2.5.3, <3',
        'numpy>=1.10, <2',
        'scipy>=0.15.1',
        'cython>=0.23.4, <1',
        # 'genometools>=0.2, <0.3',
        # 'configparser>=3.5, <4',
        # 'future >= future-0.15.3.dev0, <1',
    ],

    extras_require = {
        'test': [
            'pytest>=2.8.5, <3',
            'pytest-cov>=2.2.1, <3',
            'requests>=2.10.0, <3',
        ],
    #        'docs': ['sphinx','sphinx-rtd-theme','sphinx-argparse','mock']
    },

    #dependency_links=[
    #    'https://github.com/PythonCharmers/python-future/tarball/v0.16.xegg=future-0.15.3.dev0',
    #],

# data
    #package_data={},

	# data outside the package
    #data_files=[('my_data', ['data/data_file'])],

    ext_modules = ext_modules,

    cmdclass = cmdclass,

	# executable scripts
    entry_points = {
        'console_scripts': [
            #'ensembl_filter_fasta.py = genometools.ensembl.filter_fasta:main',
        ],
    },

)
