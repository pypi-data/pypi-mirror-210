import setuptools
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GXN",
    version="0.0.28",
    author="Sergio Peignier",
    author_email="sergio.peignier@insa-lyon.fr",
    description="Generalizable Gene Self-Expressive Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'tqdm',
        'scipy',
        'gseapy',
        'goatools',
        "kneed",
        "pygraphviz",
        "networkx",
        "grenadine"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={'': ['data/GO/*.obo',
                       'data/iDog/data/*',
                       'data/iHuman/data/*',
                       'data/iHuman/data/BRAIN/*',
                       'data/iRat/data/*',
                       'data/iRat/data/eleven_organs_four_stages/*']},
)

print(setuptools.find_packages())
