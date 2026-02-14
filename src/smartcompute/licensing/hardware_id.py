"""
Hardware fingerprinting for machine-bound licenses.

Generates a stable SHA-256 fingerprint from the machine's
hostname, MAC addresses, and CPU identifier.
"""

import hashlib
import platform
import uuid


def get_hardware_id() -> str:
    """Return a SHA-256 hex digest that uniquely identifies this machine.

    The fingerprint is derived from:
    - hostname
    - first MAC address (``uuid.getnode()``)
    - processor string

    It is intentionally *not* tied to volatile attributes (IP, disk serial)
    so that it remains stable across reboots and minor HW changes.
    """
    components = [
        platform.node(),
        hex(uuid.getnode()),
        platform.processor() or platform.machine(),
    ]
    raw = "|".join(components).encode()
    return hashlib.sha256(raw).hexdigest()
