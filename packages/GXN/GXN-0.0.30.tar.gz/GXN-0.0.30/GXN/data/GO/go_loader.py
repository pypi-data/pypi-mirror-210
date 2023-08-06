"""
Configuration file
------------------
Configuration file, contains some paths and constants that are used by other
modules from the dream5 project

Attributes:
    library_folder (str): Path to the databases folder
    id_folder (str) : Path to the ids dictionary folder
    grn_folder (str) : path to gene regulatory networks (test results) folder
    ortho_folder (str): path to orthofinder results
"""

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2021, The iDog Project"
__credits__ = ["Sergio Peignier"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

import os
from os import path
from GXN.data import GO
from goatools.obo_parser import GODag

library_folder = "/"+path.join(*os.path.abspath(GO.__file__).split("/")[:-1])
go_file = path.join(library_folder,"go-basic.obo")
go_slim_file = path.join(library_folder,"goslim_generic.obo")

def load_go(slim=False):
    if slim:
        obodag = GODag(go_slim_file)
    else:
        obodag = GODag(go_file)
    return obodag
