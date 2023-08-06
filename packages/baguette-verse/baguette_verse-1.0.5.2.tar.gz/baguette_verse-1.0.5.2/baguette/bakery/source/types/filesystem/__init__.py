"""
This package defines the graph-related subclasses that modelize interaction with filesystem.
"""

from .....logger import logger

__all__ = ["entities", "relations", "integration"]





logger.info("Finalizing {} library.".format(__name__.rpartition(".")[2]))

from .entities import *
from .relations import *