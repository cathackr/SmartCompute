"""
SmartCompute — toolkit OSS de monitoreo de host y análisis de protocolos OT/ICS
===============================================================================

Componentes:
  - core: monitoreo de host (psutil), análisis OSI, reportes HTML, API/CLI
  - industrial: parsers de protocolos industriales (Modbus, EtherNet/IP,
    PROFINET, CAN, LonWorks, DeviceNet)

Usage::

    import smartcompute
    print(smartcompute.__version__)
"""

from smartcompute._version import __version__

__all__ = ["__version__"]
