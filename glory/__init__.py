import importlib.metadata
from pathlib import Path

from .data.read_config import ConfigReader
from .data.read_data import DataLoader
from .data.write_outputs import write_outputs
from .method.supply_curve import SupplyCurve
from .method.lp import lp_model, lp_solution
from .utils.diagnostics import diagnostics
from .utils.logger import init_logger
from .utils.cleanup import cleanup
from .utils.install_supplement import get_example_data, DEFAULT_DOWNLOAD_DIR
from .model import execute, run_model


__version__ = importlib.metadata.version(__package__ or __name__)

default_download_dir = DEFAULT_DOWNLOAD_DIR
