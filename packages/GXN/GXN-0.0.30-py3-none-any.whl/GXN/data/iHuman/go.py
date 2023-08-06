"""
Load GO dataset
---------------

Loads GO h. sapiens datasets

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

from GXN.data.iHuman.configuration import library_folder
from os.path import join
from pandas import read_csv

def load_go():
    """
    Load human GO

    Returns:
        pandas.DataFrame: H. Sapiens GOs

    """
    gos = read_csv(join(library_folder, "mart_export.txt"),sep="\t",header=0)
    return(gos)

if __name__ == '__main__':
    print("Loading GO data")
    print(load_go().head())
