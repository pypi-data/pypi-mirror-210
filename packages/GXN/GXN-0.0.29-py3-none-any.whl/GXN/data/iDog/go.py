"""
Load GO dataset
---------------

Loads GO datasets

Example:
    Test the example by running this file::

        $ python gene_expression.py
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

def load_go():
    """
    Load dog GOs

    Returns:
        pandas.DataFrame: Dog GOs

    Examples:
        >>> tfscofactors = load_cofactors()
        >>> tfscofactors.head()


    """
    gos = read_csv(join(library_folder, "mart_export.txt"),sep="\t",header=0)
    return(gos)

if __name__ == '__main__':
    print("Loading GO data")
    print(load_go().head())
