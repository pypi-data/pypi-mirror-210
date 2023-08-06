"""
Load gene expression datasets
-----------------------------

Loads gene expression datasets

"""

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2023, GXN Project"
__credits__ = ["Sergio Peignier", "Elean Pauliat"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

from GXN.data.iHuman.configuration import library_folder
from GXN.data.iHuman.tf import load_tfs_cofactors
from os.path import join
from pandas import read_csv

def load_sensory_neurons_IPS(path_sensory_neurons_IPS,gene_name_as_id = False):
    """
    Load the sensory_neurons_IPS human dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_sensory_neurons_IPS (string): path to the sensory_neurons_IPS dataset
        gene-gene_name_as_id (bool): gene names used as row ids or not


    Returns:
        pandas.DataFrame: gene expression dataset
        rows represent genes and columns represent conditions


    """
    expr_data = read_csv(join(library_folder,"sensory_neurons_IPS", "E-ENAD-33-query-results.tpms.tsv"),
                         header=0,
                         index_col=0,
                         comment="#",
                         sep="\t")
    if gene_name_as_id:
        expr_data.index = expr_data["Gene Name"]
        del expr_data["Gene Name"]
    # replace row index with corresponding value in dictionary
    return expr_data.fillna(0)

def load_tfs_sensory_neurons_IPS(path_sensory_neurons_IPS):
    """
    Load sensory neurons IPS TFs gene expressions (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_sensory_neurons_IPS (string): path to the sensory_neurons_IPS dataset

    Returns:
        pandas.DataFrame: TFs gene expression dataset
        rows represent genes and columns represent conditions

    """
    X = load_sensory_neurons_IPS()
    tfs = load_tfs_cofactors()["Ensembl"]
    X_tfs = X.loc[list(set(tfs).intersection(X.index))]
    return X_tfs

def load_macrophage_immune_response(path_macrophage_immune_response,
                                    gene_name_as_id = False):
    """
    Load the macrophage immune response human dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_macrophage_immune_response: path to the macrophage_immune_response database
        gene_name_as_id: gene names used as row ids or not

    Returns:
        pandas.DataFrame: gene expression dataset
        rows represent genes and columns represent conditions

    """
    expr_data = read_csv(join(library_folder,"macrophage_immune_response", "E-ENAD-41-query-results.tpms.tsv"),
                         header=0,
                         index_col=0,
                         comment="#",
                         sep="\t")
    if gene_name_as_id:
        expr_data.index = expr_data["Gene Name"]
        del expr_data["Gene Name"]
    # replace row index with corresponding value in dictionary
    return expr_data.fillna(0)

def load_tfs_macrophage_immune_response(path_macrophage_immune_response):
    """
    Load macrophage immune response TFs dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_macrophage_immune_response (string): path to the macrophage_immune_response database

    Returns:
        pandas.DataFrame: TFs gene expression dataset
        rows represent genes and columns represent conditions

    """
    X = load_macrophage_immune_response(path_macrophage_immune_response)
    tfs = load_tfs_cofactors()["Ensembl"]
    X_tfs = X.loc[list(set(tfs).intersection(X.index))]
    return X_tfs


def load_Human_developmental_biology_resource(path_Human_developmental_biology_resource,
                                              gene_name_as_id = False):
    """
    Load the Human_developmental_biology human dataset  (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_Human_developmental_biology_resource (str): path to the Human_developmental_biology_resource database
        gene-gene_name_as_id (bool): gene names used as row ids or not

    Returns:
        pandas.DataFrame: gene expression dataset
        rows represent genes and columns represent conditions

    """
    expr_data = read_csv(join(library_folder,"Human_developmental_biology_resource", "E-MTAB-4840-query-results.tpms.tsv"),
                         header=0,
                         index_col=0,
                         comment="#",
                         sep="\t")
    if gene_name_as_id:
        expr_data.index = expr_data["Gene Name"]
        del expr_data["Gene Name"]
    return expr_data.fillna(0)

def load_tfs_Human_developmental_biology_resource(path_Human_developmental_biology_resource):
    """
    Load Human_developmental_biology TFs dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_Human_developmental_biology_resource (string): path to the Human_developmental_biology_resource database

    Returns:
        pandas.DataFrame: TFs gene expression dataset
        rows represent genes and columns represent conditions
    """
    X = load_Human_developmental_biology_resource(path_Human_developmental_biology_resource)
    tfs = load_tfs_cofactors()["Ensembl"]
    X_tfs = X.loc[list(set(tfs).intersection(X.index))]
    return X_tfs



def load_465_lymphoblastoid_cell_lines(path_465_lymphoblastoid_cell_lines,
                                       gene_name_as_id = False):
    """
    Load the 465_lymphoblastoid_cell_lines human dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Args:
        path_465_lymphoblastoid_cell_lines (str): Path to the 465_lymphoblastoid_cell_lines dataset
        gene_name_as_id (bool): should gene names be used as row ids or not


    Returns:
        pandas.DataFrame: gene expression dataset
        rows represent genes and columns represent conditions

    """
    expr_data = read_csv(join(path_465_lymphoblastoid_cell_lines, "E-GEUV-1-query-results.tpms.tsv"),
                         header=0,
                         index_col=0,
                         comment="#",
                         sep="\t")
    if gene_name_as_id:
        expr_data.index = expr_data["Gene Name"]
        del expr_data["Gene Name"]
    return expr_data.fillna(0)

def load_tfs_465_lymphoblastoid_cell_lines():
    """
    Load 465_lymphoblastoid_cell_lines TFs dataset (data can be downloaded from https://gitlab.com/bf2i/gxn/-/tree/main/GXN/data/iHuman/data)

    Returns:
        pandas.DataFrame: TFs gene expression dataset
        rows represent genes and columns represent conditions

    """
    X = load_465_lymphoblastoid_cell_lines()
    tfs = load_tfs_cofactors()["Ensembl"]
    X_tfs = X.loc[list(set(tfs).intersection(X.index))]
    return X_tfs

def load_allen_aging_dementia_tbi_study(folder_allen,normalized=True):
    """
    Load the Allen aging dementia TBI study from its folder

    Args:
        folder_allen (string): path to the Allen dataset (can be downloaded from https://aging.brain-map.org/api/v2/well_known_file_download/502999992)
        normalized (bool): Whether the normalized or unormalized gene expression data should be loaded.

    Returns:
        pandas.DataFrame: gene expression data
        rows represent genes and columns represent conditions

    """
    if normalized:
        file_path = join(folder_allen,'fpkm_table_normalized.csv')
        expr_data = read_csv(file_path,index_col=0,)
    else:
        file_path = join(folder_allen,'fpkm_table_unnormalized.csv')
        expr_data = read_csv(file_path,
                             index_col=0,)
    genes_info = read_csv(join(folder_allen,'rows-genes.csv'))
    expr_data.index = genes_info["gene_symbol"]
    return expr_data


if __name__ == '__main__':
    print("")
