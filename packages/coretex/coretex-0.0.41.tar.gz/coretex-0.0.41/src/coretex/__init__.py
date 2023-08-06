# Internal - not for outside use
from ._configuration import _syncConfigWithEnv
_syncConfigWithEnv()


from ._logger import _initializeDefaultLogger
_initializeDefaultLogger()


# Use this only
from .coretex import *
