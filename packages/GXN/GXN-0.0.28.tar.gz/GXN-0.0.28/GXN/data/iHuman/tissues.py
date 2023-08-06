"""
Load gene expression tissues datasets
-------------------------------------

Loads gene expression tissues datasets

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

from GXN.data.iHuman.configuration import library_folder
from os.path import join
from pandas import read_csv,merge,concat

def load_allen_aging_dementia_tbi_study_information():
    """
    Load datasets tissues

    Returns:
        pandas.DataFrame: Allen aging dementia TBI study libraries description

    """
    folder_allen = join(library_folder,
                        "BRAIN")
    patient_info = read_csv(join(folder_allen,'DonorInformation.csv'))
    libraries_info  = read_csv(join(folder_allen,'columns-samples.csv'))
    return merge(patient_info, libraries_info, how='inner',on="donor_id")

def load_kegg_alzheimer_pathway():
    """
    Load list of KEGG genes involved in Alzheimer Pathway.

    Returns:
        pandas.DataFrame: information regarding genes in Alzheimer pathway from KEGG
    """
    folder_brain = join(library_folder,
                        "BRAIN")
    kegg = read_csv(join(folder_brain,'kegg_alzheimer.csv'),sep="*",comment="#",index_col=0)
    genes_info = read_csv(join(folder_brain,'rows-genes.csv'))
    genes_info.index = genes_info["gene_entrez_id"]
    return concat((kegg,genes_info.loc[kegg.index]),axis=1)

if __name__ == '__main__':
    print("Loading tissues data")
    print(load_allen_aging_dementia_tbi_study_information())
    print(load_kegg_alzheimer_pathway())
