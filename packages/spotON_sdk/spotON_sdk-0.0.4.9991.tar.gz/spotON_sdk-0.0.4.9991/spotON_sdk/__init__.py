"""
The spotON_sdk package provides tools for interacting with the spotON API.

This package includes modules for authenticating with the API, sending requests,
and processing responses. It also includes utility functions for working with
the data returned by the API.
"""


from .Logic import *
from .data_helpers import *
from . import spotON_controller


__version__ = "0.0.4.9991"
__all__ = [name for name in dir() if not name.startswith('_')] #type: ignore
