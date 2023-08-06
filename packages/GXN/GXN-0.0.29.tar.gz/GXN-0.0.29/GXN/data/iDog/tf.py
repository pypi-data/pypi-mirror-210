"""
C. familiaris TF datasets
--------------------------

This module allows to load lists of Transcription Factors for the iDog dataset
To use this library you should also have the related datasets.

Example:
    Test the example by running this file::

        $ python tf.py

Todo:

"""

from os.path import join
from pandas import read_csv,concat


__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2023, The GXN Project"
__credits__ = ["Sergio Peignier"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"


from GXN.data.iDog.configuration import library_folder
from os.path import join
from pandas import read_csv

def load_tfs():
    """
    Load dog TFs

    Returns:
        pandas.DataFrame: Dog TFs

    Examples:
        >>> tfs = load_tfs()
        >>> tfs.head()


    """
    tfs = read_csv(join(library_folder, "Canis_familiaris_TF.txt"),sep="\t",header=0)
    return tfs


def load_cofactors():
    """
    Load dog TFs Cofactors

    Returns:
        pandas.DataFrame: Dog TFs cofactors

    Examples:
        >>> cofactors = load_cofactors()
        >>> cofactors.head()


    """
    cofactors = read_csv(join(library_folder, "Canis_familiaris_TF_cofactors.txt"),header=0,sep="\t")
    return cofactors


def load_tfs_cofactors():
    """
    Load dog TFs and Cofactors

    Returns:
        pandas.DataFrame: Dog TFs and Cofactors

    Examples:
        >>> tfscofactors = load_cofactors()
        >>> tfscofactors.head()


    """
    cofactors = load_cofactors()
    tfs = load_tfs()
    return concat((cofactors,tfs))


if __name__ == '__main__':
    print("Loading TFs data")
    print(load_tfs_cofactors())
