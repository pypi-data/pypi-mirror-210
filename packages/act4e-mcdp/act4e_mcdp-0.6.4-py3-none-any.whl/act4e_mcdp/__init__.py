import coloredlogs

coloredlogs.install(level="DEBUG")

from logging import getLogger, DEBUG

logger = getLogger(__name__)
logger.setLevel(DEBUG)

# __version__ = "0.2.1"

from .loading import *
from .main_solve_mcdp import *
from .main_solve_dp import *
from .solution_interface import *
from .nameddps import *
from .primitivedps import *
from .posets import *
from .download import *
from .main_solve_dp_queries import *
