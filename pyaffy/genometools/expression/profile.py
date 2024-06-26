# Copyright (c) 2016 Florian Wagner
#
# This file is part of GenomeTools.
#
# GenomeTools is free software: you can redistribute it and/or modify
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

"""Module containing the `ExpProfile` class."""
"""Deprecated. Use `genometools.expression.matrix.ExpMatrix` instead."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
_oldstr = str
from builtins import *

import logging
import importlib
import hashlib
from typing import Iterable

import six
import pandas as pd
import warnings
import numpy as np

from . import ExpGene, ExpGeneTable
matrix = importlib.import_module('.matrix', package='genometools.expression')
# "from . import matrix" does not work, due to cyclical imports

logger = logging.getLogger(__name__)


@warnings.deprecated('Use `genometools.expression.matrix.ExpMatrix` instead.')
class ExpProfile(pd.Series):
    """A gene expression profile.

    This class inherits from `pandas.Series`.

    Parameters
    ----------
    x : 1-dimensional `numpy.ndarray`
        See :attr:`x` attribute.

    Keyword-only Parameters
    -----------------------
    genes : list or tuple of str
        See :attr:`genes` attribute.
    name : str
        See :attr:`name` attribute.

    Additional Parameters
    ---------------------
    All `pandas.Series` parameters.

    Attributes
    ----------
    x : 1-dimensional `numpy.ndarray`
        The vector with expression values.
    genes : `pandas.Index`
        Alias for :attr:`pandas.Series.index`. Contains the names of the genes
        in the matrix.
    label : str
        Alias for :attr:`pandas.Series.name`. The sample label.
    """
    def __init__(self, *args,
                 x: np.ndarray = None,
                 genes: Iterable[str] = None, label: str = None,
                 gene_label: str = None,
                 **kwargs):

        # check if user provided "x" keyword argument
        if x is not None:
            if 'data' in kwargs:
                raise ValueError(
                    'Cannot specify both "x" and "data" arguments.')
            if x.ndim != 1:
                raise ValueError('Must provide a one-dimensional array.')
            kwargs['data'] = x

        # call base class constructor
        pd.Series.__init__(self, *args, **kwargs)

        if genes is not None:
            # set (overwrite) index with user-provided list
            self.index = genes

        if label is not None:
            # set (overwrite) series name with user-provided sample label
            self.name = label

        # set index name (default: "Genes")
        if gene_label is not None:
            self.index.name = gene_label
        elif self.index.name is None:
            self.index.name = 'Genes'

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) is type(other):
            return (self.label == other.label and
                    self.index.equals(other.index) and
                    self.equals(other))
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s instance (label="%s", p=%d, hash="%s">' \
               % (self.__class__.__name__, self._label_str,
                  self.p, self.hash)

    #def __str__(self):
    #    if self.label is not None:
    #        label_str = self._label_str
    #    else:
    #        label_str = '(unlabeled)'
    #    return '<%s %s with p=%d genes>'  \
    #           % (self.__class__.__name__, label_str, self.p)

    @property
    def _label_str(self):
        return str(self.label) if self.label is not None else ''

    @property
    def _constructor(self):
        return ExpProfile

    @property
    def _constructor_expanddim(self):
        return matrix.ExpMatrix

    @property
    def hash(self):
        # warning: involves copying all the data
        gene_str = ','.join([str(g) for g in self.genes])
        data_str = ';'.join([self._label_str, gene_str]) + ';'
        data = data_str.encode('UTF-8') + self.x.tobytes()
        return str(hashlib.md5(data).hexdigest())

    @property
    def p(self):
        """The number of genes."""
        return self.shape[0]

    @property
    def genes(self):
        """Alias for `Series.index`."""
        return self.index

    @genes.setter
    def genes(self, gene_list):
        self.index = gene_list

    @property
    def label(self):
        """Alias for `Series.name`."""
        return self.name

    @label.setter
    def label(self, label):
        self.name = label

    @property
    def x(self):
        """Alias for `Series.values`."""
        return self.values

    @x.setter
    def x(self, x):
        self.x[:] = x


    def sort_genes(self, inplace=False):
        """Sort the rows of the profile alphabetically by gene name.

        Parameters
        ----------
        inplace: bool, optional
            If set to True, perform the sorting in-place.

        Returns
        -------
        None

        Notes
        -----
        pandas 0.18.0's `Series.sort_index` method does not support the
        ``kind`` keyword, which is needed to select a stable sort algorithm.
        """
        # kind = 'quicksort'
        # if stable:
        #    kind = 'mergesort'
        self.sort_index(inplace=inplace)


    def filter_genes(self, gene_names : Iterable[str]):
        """Filter the expression matrix against a set of genes.

        Parameters
        ----------
        gene_names: list of str
            The genome to filter the genes against.

        Returns
        -------
        ExpMatrix
            The filtered expression matrix.
        """

        filt = self.loc[self.index & gene_names]
        return filt


    @classmethod
    def read_tsv(cls, filepath_or_buffer: str, gene_table: ExpGeneTable = None,
                 encoding='UTF-8'):
        """Read expression profile from a tab-delimited text file.

        Parameters
        ----------
        path: str
            The path of the text file.
        gene_table: `ExpGeneTable` object, optional
            The set of valid genes. If given, the genes in the text file will
            be filtered against this set of genes. (None)
        encoding: str, optional
            The file encoding. ("UTF-8")

        Returns
        -------
        `ExpProfile`
            The expression profile.
        """
        # "squeeze = True" ensures that a pd.read_tsv returns a series
        # as long as there is only one column
        e = cls(pd.read_csv(filepath_or_buffer, sep='\t',
                            index_col=0, header=0,
                            encoding=encoding, squeeze=True))

        if gene_table is not None:
            # filter genes
            e = e.filter_genes(gene_table.gene_names)

        return e


    def write_tsv(self, path, encoding='UTF-8'):
        """Write expression matrix to a tab-delimited text file.

        Parameters
        ----------
        path: str
            The path of the output file.
        encoding: str, optional
            The file encoding. ("UTF-8")

        Returns
        -------
        None
        """
        assert isinstance(path, (str, _oldstr))
        assert isinstance(encoding, (str, _oldstr))

        sep = '\t'
        if six.PY2:
            sep = sep.encode('UTF-8')

        self.to_csv(
            path, sep=sep, float_format='%.5f', mode='w',
            encoding=encoding, header=True
        )

        logger.info('Wrote expression profile "%s" with %d genes to "%s".',
                    self.name, self.p, path)
