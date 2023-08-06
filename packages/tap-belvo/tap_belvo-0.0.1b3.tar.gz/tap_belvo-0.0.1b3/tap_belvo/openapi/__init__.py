"""OpenAPI 3.0.0 specification for the Belvo API."""

from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from typing import Any

if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

logger = logging.getLogger(__name__)


@lru_cache(maxsize=None)
def load_openapi() -> dict[str, Any]:
    """Load the OpenAPI specification from the package.

    Returns:
        The OpenAPI specification as a dict.
    """
    logger.info("Loading OpenAPI spec from package")
    filename = "BelvoOpenFinanceApiSpec.json"
    with importlib_resources.files(__package__).joinpath(filename).open() as f:
        return json.load(f)
