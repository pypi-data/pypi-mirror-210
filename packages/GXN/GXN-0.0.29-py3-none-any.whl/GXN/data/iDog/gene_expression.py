"""
Load gene expression datasets
-----------------------------

Loads gene expression datasets

Example:
    Test the example by running this file::

        $ python gene_expression.py
"""

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2023, GXN Project"
__credits__ = ["Sergio Peignier"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

from GXN.data.iDog.configuration import library_folder
from GXN.data.iDog.tf import load_tfs_cofactors
from os.path import join
from pandas import read_csv

def load_gene_expression():
    """
    Load in iDog dataset

    Returns:
        pandas.DataFrame: iDog gene expression dataset
        rows represent genes and columns represent conditions

    Examples:
        >>> df_idog = load_idog()
        >>> df_idog.head()


    """
    expr_data = read_csv(join(library_folder, "gene_expression_matrix.csv"),
                         header=0,
                         index_col=0)
    return expr_data


def load_tfs_gene_expression():
    """
    Load iDog TFs dataset

    Returns:
        pandas.DataFrame: iDog TFs gene expression dataset
        rows represent genes and columns represent conditions

    Examples:
        >>> df_idog = load_idog()
        >>> df_idog.head()


    """
    X = load_gene_expression()
    tfs = load_tfs_cofactors()["Ensembl"]
    X_tfs = X.loc[list(set(tfs).intersection(X.index))]
    return X_tfs

if __name__ == '__main__':
    print("Loading gene expression data")
    print(load_gene_expression().head())
