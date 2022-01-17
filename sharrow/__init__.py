from xarray import DataArray

from . import example_data
from ._version import version as __version__
from .dataset import Dataset
from .digital_encoding import array_decode, array_encode
from .relationships import DataTree, Relationship
from .table import Table, concat_tables
