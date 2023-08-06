"""
MIT License

Copyright (c) 2021 community-fabric

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .graphs import IPFDiagram
from .input_models import (
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

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

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

__version__ = importlib_metadata.version("ipfabric_diagrams")
