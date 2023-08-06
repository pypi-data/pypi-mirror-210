import sys

from module_qc_database_tools._version import __version__

if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources
data = resources.files("module_qc_database_tools") / "data"

__all__ = ("__version__", "data")
