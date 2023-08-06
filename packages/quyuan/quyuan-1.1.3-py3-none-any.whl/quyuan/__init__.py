"""a utility for illustrating human and other species chromosomes"""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("quyuan")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
