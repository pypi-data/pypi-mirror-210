"""
Load gene expression tissues information
----------------------------------------

Loads gene expression tissues datasets

Example:
    Test the example by running this file::

        $ python tissues.py
"""

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2023, The GXN Project"
__credits__ = ["Sergio Peignier"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

from GXN.data.iDog.configuration import library_folder
from os.path import join
from pandas import read_csv

def load_tissue():
    """
    Load datasets tissues

    Returns:
        pandas.DataFrame: iDog libraries tissues

    Examples:
        >>> df_tissue = load_tissue()
        >>> df_tissue.head()


    """
    tissues = read_csv(join(library_folder, "tissues_clean.csv"),header=0,index_col=0)
    return tissues

if __name__ == '__main__':
    print("Loading tissues data")
    print(load_tissue().head())
