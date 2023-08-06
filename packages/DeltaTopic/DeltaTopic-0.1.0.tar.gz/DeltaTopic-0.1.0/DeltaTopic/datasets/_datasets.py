from pathlib import Path
from typing import Optional, Union
from scanpy import read

url_datadir = "https://github.com/causalpathlab/DeltaTopic/tree/benchmark_dev/"

def toy_data(file_path: Union[str, Path] = "DeltaTopic/datasets/toy_data.h5ad"):
    """toy_example.

    Arguments
    ---------
    file_path
        Path where to save dataset and read it from.

    Returns
    -------
    Returns `adata` object
    """
    url = f"{url_datadir}DeltaTopic/datasets/toy_data.h5ad"
    adata = read(file_path)
    #adata.var_names_make_unique()
    return adata



