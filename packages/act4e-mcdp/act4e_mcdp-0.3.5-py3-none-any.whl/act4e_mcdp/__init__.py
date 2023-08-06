import coloredlogs

coloredlogs.install(level="DEBUG")

from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

# __version__ = "0.2.1"

from .loading import *
from .structures import *
from .main import *
from .solution_interface import *
