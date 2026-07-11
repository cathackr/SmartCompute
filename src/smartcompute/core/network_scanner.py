"""
Network Host Discovery for SmartCompute Dashboard.

Discovers hosts on the local network via ARP cache (passive) and
ping sweep (active). No root privileges required.
"""

from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import psutil


@dataclass
class DiscoveredHost:
    """A host discovered on the local network."""

    ip: str
    mac: str = ""
    hostname: str = ""
    vendor: str = ""
    status: str = "reachable"  # reachable | stale | unreachable
    interface: str = ""
    source: str = "arp"  # arp | ping | both
    last_seen: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "ip": self.ip,
            "mac": self.mac,
            "hostname": self.hostname,
            "vendor": self.vendor,
            "status": self.status,
            "interface": self.interface,
            "source": self.source,
            "last_seen": self.last_seen,
        }


class NetworkHostScanner:
    """Discovers hosts on local network subnets."""

    def __init__(self) -> None:
        self._hosts: Dict[str, DiscoveredHost] = {}
        self._scan_lock = asyncio.Lock()
        self._scan_in_progress = False
        self._last_scan_time: float = 0
        self._mac_vendor_db = _build_vendor_db()

    # ------------------------------------------------------------------
    # Subnet detection
    # ------------------------------------------------------------------

    def detect_local_subnets(self) -> List[str]:
        """Return list of local IPv4 subnets as CIDR strings."""
        subnets: List[str] = []
        skip_prefixes = ("lo", "docker", "veth", "br-", "virbr")
        for name, addrs in psutil.net_if_addrs().items():
            if name.startswith(skip_prefixes):
                continue
            stats = psutil.net_if_stats().get(name)
            if stats and not stats.isup:
                continue
            for a in addrs:
                if a.family != socket.AF_INET or not a.netmask:
                    continue
                try:
                    net = ipaddress.IPv4Network(
                        f"{a.address}/{a.netmask}", strict=False
                    )
                    if net.is_loopback or net.prefixlen > 30 or net.prefixlen < 20:
                        continue
                    subnets.append(str(net))
                except ValueError:
                    continue
        return subnets

    def _get_default_gateway(self) -> Optional[str]:
        """Parse default gateway from ``ip route``."""
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                parts = result.stdout.strip().split()
                if len(parts) > 2:
                    return parts[2]
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # ARP cache (passive, fast)
    # ------------------------------------------------------------------

    async def read_arp_cache(self) -> Dict[str, DiscoveredHost]:
        """Read OS ARP/neighbour table — fast, no root needed."""
        hosts: Dict[str, DiscoveredHost] = {}

        # Try `ip neigh show` first (includes state)
        try:
            proc = await asyncio.create_subprocess_exec(
                "ip", "neigh", "show",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
            for line in stdout.decode().splitlines():
                parts = line.split()
                if len(parts) < 4:
                    continue
                ip_addr = parts[0]
                # skip IPv6
                if ":" in ip_addr and "." not in ip_addr:
                    continue
                mac = ""
                iface = ""
                state = "reachable"
                for i, tok in enumerate(parts):
                    if tok == "lladdr" and i + 1 < len(parts):
                        mac = parts[i + 1].lower()
                    if tok == "dev" and i + 1 < len(parts):
                        iface = parts[i + 1]
                if not mac or mac == "00:00:00:00:00:00":
                    continue
                # Map kernel states
                state_token = parts[-1].upper()
                if state_token in ("REACHABLE",):
                    state = "reachable"
                elif state_token in ("STALE", "DELAY", "PROBE"):
                    state = "stale"
                elif state_token in ("FAILED", "INCOMPLETE"):
                    continue  # skip unresolved
                else:
                    state = "reachable"
                hostname = await self._reverse_dns(ip_addr)
                hosts[ip_addr] = DiscoveredHost(
                    ip=ip_addr,
                    mac=mac,
                    hostname=hostname,
                    vendor=self._get_mac_vendor(mac),
                    status=state,
                    interface=iface,
                    source="arp",
                    last_seen=time.time(),
                )
        except Exception:
            # Fallback: `arp -a`
            try:
                proc = await asyncio.create_subprocess_exec(
                    "arp", "-a",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
                for line in stdout.decode().splitlines():
                    m = re.search(
                        r"\(([\d.]+)\)\s+at\s+([a-fA-F0-9:]{17})", line
                    )
                    if not m:
                        continue
                    ip_addr = m.group(1)
                    mac = m.group(2).lower()
                    iface_m = re.search(r"on\s+(\w+)", line)
                    iface = iface_m.group(1) if iface_m else ""
                    hostname = await self._reverse_dns(ip_addr)
                    hosts[ip_addr] = DiscoveredHost(
                        ip=ip_addr,
                        mac=mac,
                        hostname=hostname,
                        vendor=self._get_mac_vendor(mac),
                        status="reachable",
                        interface=iface,
                        source="arp",
                        last_seen=time.time(),
                    )
            except Exception:
                pass

        # Merge into cache
        for ip, host in hosts.items():
            existing = self._hosts.get(ip)
            if existing:
                existing.mac = host.mac or existing.mac
                existing.hostname = host.hostname or existing.hostname
                existing.vendor = host.vendor or existing.vendor
                existing.status = host.status
                existing.interface = host.interface or existing.interface
                if existing.source == "ping" and host.source == "arp":
                    existing.source = "both"
                existing.last_seen = host.last_seen
            else:
                self._hosts[ip] = host

        return self._hosts

    # ------------------------------------------------------------------
    # Ping sweep (active, on-demand)
    # ------------------------------------------------------------------

    async def ping_sweep(self, subnet: Optional[str] = None) -> Dict[str, DiscoveredHost]:
        """Active ping sweep of a /24 (or detected) subnet."""
        if self._scan_lock.locked():
            return self._hosts

        async with self._scan_lock:
            self._scan_in_progress = True
            try:
                subnets = [subnet] if subnet else self.detect_local_subnets()
                sem = asyncio.Semaphore(50)

                for net_str in subnets:
                    net = ipaddress.IPv4Network(net_str, strict=False)
                    if net.prefixlen < 20:
                        continue  # refuse >4094 hosts
                    tasks = []
                    for addr in net.hosts():
                        tasks.append(self._ping_host(str(addr), sem))
                    results = await asyncio.gather(*tasks)
                    for host in results:
                        if host is None:
                            continue
                        existing = self._hosts.get(host.ip)
                        if existing:
                            existing.status = "reachable"
                            existing.last_seen = host.last_seen
                            if existing.source == "arp":
                                existing.source = "both"
                            if not existing.hostname:
                                existing.hostname = host.hostname
                        else:
                            self._hosts[host.ip] = host

                self._last_scan_time = time.time()
            finally:
                self._scan_in_progress = False

        return self._hosts

    async def _ping_host(
        self, ip: str, sem: asyncio.Semaphore
    ) -> Optional[DiscoveredHost]:
        async with sem:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "ping", "-c", "1", "-W", "1", ip,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await asyncio.wait_for(proc.communicate(), timeout=3)
                if proc.returncode == 0:
                    hostname = await self._reverse_dns(ip)
                    return DiscoveredHost(
                        ip=ip,
                        hostname=hostname,
                        status="reachable",
                        source="ping",
                        last_seen=time.time(),
                    )
            except Exception:
                pass
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _reverse_dns(self, ip: str) -> str:
        loop = asyncio.get_running_loop()
        try:
            result = await asyncio.wait_for(
                loop.run_in_executor(None, socket.gethostbyaddr, ip),
                timeout=1,
            )
            return result[0]
        except Exception:
            return ""

    def _get_mac_vendor(self, mac: str) -> str:
        if not mac:
            return ""
        prefix = mac[:8].lower()
        return self._mac_vendor_db.get(prefix, "")

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def get_cached_hosts(self) -> dict:
        """Return JSON-serialisable snapshot of discovered hosts."""
        hosts_list = sorted(
            self._hosts.values(), key=lambda h: _ip_sort_key(h.ip)
        )
        reachable = sum(1 for h in hosts_list if h.status == "reachable")
        return {
            "hosts": [h.to_dict() for h in hosts_list],
            "total": len(hosts_list),
            "reachable": reachable,
            "scan_in_progress": self._scan_in_progress,
            "last_scan_time": self._last_scan_time or None,
            "subnets": self.detect_local_subnets(),
            "gateway": self._get_default_gateway(),
        }


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_scanner: Optional[NetworkHostScanner] = None


def get_scanner() -> NetworkHostScanner:
    """Return (or create) the module-level scanner singleton."""
    global _scanner
    if _scanner is None:
        _scanner = NetworkHostScanner()
    return _scanner


# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------


def _ip_sort_key(ip: str):
    """Sort IPs numerically."""
    try:
        return ipaddress.IPv4Address(ip)
    except ValueError:
        return ipaddress.IPv4Address("255.255.255.255")


def _build_vendor_db() -> Dict[str, str]:
    """Common OUI prefixes — same DB as monitor.py."""
    return {
        "00:00:0c": "Cisco Systems",
        "00:01:42": "Parallels Inc",
        "00:03:93": "Apple Inc",
        "00:04:20": "Hitachi Ltd",
        "00:05:02": "Apple Inc",
        "00:0a:27": "Apple Inc",
        "00:0c:29": "VMware Inc",
        "00:0f:4b": "Realtek Semiconductor",
        "00:11:25": "Intel Corporate",
        "00:13:72": "Dell Inc",
        "00:15:5d": "Microsoft Corporation",
        "00:16:3e": "Xensource Inc",
        "00:17:fa": "Broadcom Corporation",
        "00:1b:21": "Intel Corporate",
        "00:1c:23": "Cisco Systems",
        "00:1c:25": "Broadcom Corporation",
        "00:1e:68": "Cisco Systems",
        "00:21:70": "Cisco Systems",
        "00:22:48": "Cisco Systems",
        "00:23:ea": "Cisco Systems",
        "00:25:90": "Cisco Systems",
        "00:50:56": "VMware Inc",
        "08:00:27": "Oracle VirtualBox",
        "0c:54:15": "Apple Inc",
        "10:dd:b1": "Apple Inc",
        "14:10:9f": "Apple Inc",
        "18:03:73": "Dell Inc",
        "20:c9:d0": "Apple Inc",
        "28:cf:e9": "Apple Inc",
        "2c:f0:5d": "Micro-Star Intl",
        "30:9c:23": "Micro-Star Intl",
        "34:97:f6": "ASUSTek Computer",
        "3c:07:54": "Apple Inc",
        "40:8d:5c": "GIGA-BYTE Technology",
        "40:a8:f0": "Apple Inc",
        "44:38:39": "Cumulus Networks",
        "48:21:0b": "Dell Inc",
        "4c:cc:6a": "Netgear",
        "50:6b:4b": "Lenovo",
        "52:54:00": "QEMU Virtual NIC",
        "54:bf:64": "Dell Inc",
        "58:11:22": "ASUSTek Computer",
        "60:03:08": "Apple Inc",
        "64:00:6a": "Dell Inc",
        "68:5b:35": "Apple Inc",
        "6c:4b:90": "Lenovo",
        "70:56:81": "Apple Inc",
        "74:46:a0": "TP-Link",
        "78:4f:43": "Apple Inc",
        "7c:10:c9": "ASUSTek Computer",
        "80:61:5f": "Hewlett-Packard",
        "84:38:35": "Apple Inc",
        "88:63:df": "Apple Inc",
        "8c:85:90": "Apple Inc",
        "90:72:40": "Apple Inc",
        "94:e6:f7": "Apple Inc",
        "98:90:96": "Dell Inc",
        "9c:b6:d0": "Rivet Networks",
        "a0:36:9f": "Intel Corporate",
        "a4:34:d9": "Intel Corporate",
        "a4:83:e7": "Apple Inc",
        "a8:a1:59": "Netgear",
        "ac:87:a3": "Apple Inc",
        "b0:25:aa": "Huawei",
        "b4:2e:99": "Hewlett-Packard",
        "b8:09:8a": "Apple Inc",
        "b8:e8:56": "Apple Inc",
        "c4:2c:03": "Apple Inc",
        "c8:2a:14": "Apple Inc",
        "cc:46:d6": "Cisco Systems",
        "d0:25:44": "Apple Inc",
        "d4:9a:20": "Apple Inc",
        "d8:cb:8a": "Micro-Star Intl",
        "dc:a9:04": "Apple Inc",
        "e0:ac:cb": "Apple Inc",
        "e4:54:e8": "Dell Inc",
        "e4:ce:8f": "Apple Inc",
        "e8:06:88": "Apple Inc",
        "ec:f4:bb": "Apple Inc",
        "f0:18:98": "Apple Inc",
        "f4:5c:89": "Apple Inc",
        "f8:1e:df": "Apple Inc",
        "fc:25:3f": "Apple Inc",
    }
