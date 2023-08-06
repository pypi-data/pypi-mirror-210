# Mypy; for the `|` operator purpose
# Remove this __future__ import once the oldest supported Python is 3.10
from __future__ import annotations

import logging

from . import exceptions  # noqa: F401
from . import job_metadata_constants  # noqa: F401
from .bluequbit_client import BQClient
from .estimate_result import EstimateResult  # noqa: F401
from .job_result import JobResult  # noqa: F401
from .version import __version__  # noqa: F401

formatter = logging.Formatter(fmt="BQ-PYTHON-SDK - %(levelname)s - %(message)s")
# formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("bluequbit-python-sdk")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def init(api_token: str | None = None, update_config_file: bool = True) -> BQClient:
    """Returns :class:`BQClient` instance for managing jobs on BlueQubit platform.

    :param api_token: API token of the user. If ``None``, the token will be looked
                      in default configuration file ``$HOME/.config/bluequbit/config.json``.
                      If not ``None``, the token will also be saved in the same
                      default configuration file.
    :param update_config_file: if True, update default configuration file
                               if api_token is not None.
    """
    return BQClient(api_token, update_config_file)
