"""
Human TF datasets
------------------

This module allows to load lists of Transcription Factors for the H.sapiens dataset
To use this library you should also have the related datasets.

Example:
    Test the example by running this file::

        $ python tf.py

Todo:

"""


__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2023, The GXN Project"
__credits__ = ["Sergio Peignier"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

from os.path import join
from pandas import read_csv,concat
from GXN.data.iHuman.configuration import library_folder
from os.path import join
from pandas import read_csv

def load_tfs():
    """
    Load human TFs

    Returns:
        pandas.DataFrame: H. sapiens TFs

    Examples:
        >>> tfs = load_tfs()
        >>> tfs.head()


    """
    tfs = read_csv(join(library_folder, "Homo_sapiens_TF.txt"),sep="\t",header=0)
    return tfs


def load_cofactors():
    """
    Load human TFs Cofactors

    Returns:
        pandas.DataFrame: Dog TFs cofactors

    Examples:
        >>> cofactors = load_cofactors()
        >>> cofactors.head()


    """
    cofactors = read_csv(join(library_folder, "Homo_sapiens_TF_cofactors.txt"),header=0,sep="\t")
    return cofactors


def load_tfs_cofactors():
    """
    Load human TFs and Cofactors

    Returns:
        pandas.DataFrame: H. sapiens TFs and Cofactors

    Examples:
        >>> tfscofactors = load_cofactors()
        >>> tfscofactors.head()


    """
    cofactors = load_cofactors()
    tfs = load_tfs()
    return concat((cofactors,tfs))


if __name__ == '__main__':
    print("Loading TFs data")
    print(load_tfs_gene_expression())
