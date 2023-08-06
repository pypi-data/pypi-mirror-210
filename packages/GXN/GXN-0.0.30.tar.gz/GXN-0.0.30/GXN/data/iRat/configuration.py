"""
Configuration file
------------------
Configuration file, contains some paths and constants that are used by other
modules to load data from R. norvegicus

Attributes:
    library_folder (str): Path to the databases folder
    id_folder (str) : Path to the ids dictionary folder
    grn_folder (str) : path to gene regulatory networks (test results) folder
    ortho_folder (str): path to orthofinder results
"""

__author__ = "Sergio Peignier"
__copyright__ = "Copyright 2021, The iRat Project"
__credits__ = ["Sergio Peignier"]
__maintainer__ = "Sergio Peignier"
__email__ = "sergio.peignier@insa-lyon.fr"
__status__ = "pre-alpha"

from os import path
from GXN.data import iRat

library_folder = "/"+path.join(*path.abspath(iRat.__file__).split("/")[:-1])
library_folder = path.join(library_folder,"data")
