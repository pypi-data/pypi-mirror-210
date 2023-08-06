"""
For backwards compatability until ipfabric_diagrams is merged into ipfabric in v7.0.0
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

import logging

from ipfabric.diagrams import (
    IPFDiagram,
    Unicast,
    Multicast,
    Host2GW,
    Network,
    OtherOptions,
    Algorithm,
    EntryPoint,
    Layout,
    NetworkSettings,
    PathLookupSettings,
    Overlay,
    VALID_NET_PROTOCOLS,
    VALID_PATH_PROTOCOLS,
)

logger = logging.getLogger("ipfabric_diagrams")

logger.warning(
    "ipfabric_diagrams will be merged into ipfabric in v7.0.0 with backwards compatability until then.\n"
    "Please update imports from `ipfabric_diagrams` to `ipfabric.diagrams`"
)

__all__ = [
    "IPFDiagram",
    "Unicast",
    "Multicast",
    "Host2GW",
    "Network",
    "OtherOptions",
    "Algorithm",
    "Overlay",
    "icmp",
    "NetworkSettings",
    "PathLookupSettings",
    "EntryPoint",
    "VALID_NET_PROTOCOLS",
    "VALID_PATH_PROTOCOLS",
    "Layout",
]

__version__ = importlib_metadata.version(__name__)
