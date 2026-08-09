#!/usr/bin/env python3
"""
SmartCompute → Wazuh Connector  (v2 — JSON/syslog)

Protocol: RFC-3164 syslog with a flat JSON body.
Wazuh's JSON_Decoder extracts every field directly — no CEF parsing needed.

Message format on the wire:
  <PRI>Mmm DD HH:MM:SS smartcompute smartcompute: {"anomaly_type":"ot_...", ...}

Wazuh decoder (local_decoder.xml):
  program_name = smartcompute  →  JSON_Decoder plugin
"""

import json
import socket
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

_FAC_LOCAL0 = 16

_SEV = {
    "crit":   2,
    "err":    3,
    "warn":   4,
    "notice": 5,
    "info":   6,
}


def _risk_to_sev(risk: float) -> int:
    if risk >= 0.90: return _SEV["crit"]
    if risk >= 0.70: return _SEV["err"]
    if risk >= 0.50: return _SEV["warn"]
    return _SEV["notice"]


class WazuhConnector:
    """
    Sends SmartCompute anomaly events to Wazuh Manager as JSON-over-syslog.

    Wazuh manager must have in ossec.conf:
        <remote>
          <connection>syslog</connection>
          <port>514</port>
          <protocol>udp</protocol>
          <allowed-ips>10.0.0.0/8</allowed-ips>
        </remote>

    And in /var/ossec/etc/decoders/local_decoder.xml:
        <decoder name="smartcompute">
          <program_name>^smartcompute$</program_name>
        </decoder>
        <decoder name="smartcompute-json">
          <parent>smartcompute</parent>
          <prematch>\{</prematch>
          <plugin_decoder>JSON_Decoder</plugin_decoder>
        </decoder>
    """

    def __init__(
        self,
        host: str    = "localhost",
        port: int    = 514,
        protocol: str = "udp",
        facility: int = _FAC_LOCAL0,
        tag: str     = "smartcompute",
        timeout: int = 5,
    ):
        self.host     = host
        self.port     = port
        self.protocol = protocol.lower()
        self.facility = facility
        self.tag      = tag
        self.timeout  = timeout
        self.logger   = logging.getLogger(__name__)
        self._tcp_sock: Optional[socket.socket] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_anomaly_event(
        self, anomaly_data: Dict[str, Any], **_kwargs
    ) -> Dict[str, Any]:
        """Send a pre-flattened anomaly dict as JSON syslog to Wazuh."""
        risk = float(anomaly_data.get("risk_score", 0.5))
        ok   = self._emit(anomaly_data, _risk_to_sev(risk))
        return {
            "status":      "success" if ok else "error",
            "destination": f"{self.host}:{self.port}/{self.protocol}",
        }

    def test_connection(self) -> Dict[str, Any]:
        probe = {
            "anomaly_type": "connectivity_test",
            "source_host":  "smartcompute",
            "risk_score":   0.0,
            "description":  "SmartCompute→Wazuh connectivity probe",
            "is_test":      True,
        }
        result = self.send_anomaly_event(probe)
        result.update(host=self.host, port=self.port, protocol=self.protocol)
        return result

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def _emit(self, payload: Dict[str, Any], severity: int) -> bool:
        frame = self._build_frame(payload, severity)
        try:
            return self._send_udp(frame) if self.protocol == "udp" else self._send_tcp(frame)
        except Exception as exc:
            self.logger.error("Wazuh send failed: %s", exc)
            return False

    def _build_frame(self, payload: Dict[str, Any], severity: int) -> bytes:
        pri = self.facility * 8 + severity
        ts  = datetime.now(timezone.utc).strftime("%b %d %H:%M:%S")
        # Wazuh JSON_Decoder requires the JSON to start with '{'
        body = json.dumps(payload, default=str, ensure_ascii=False)
        line = f"<{pri}>{ts} smartcompute {self.tag}: {body}"
        return line.encode("utf-8", errors="replace")

    def _send_udp(self, frame: bytes) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(self.timeout)
            s.sendto(frame, (self.host, self.port))
        return True

    def _send_tcp(self, frame: bytes) -> bool:
        try:
            if self._tcp_sock is None:
                self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._tcp_sock.settimeout(self.timeout)
                self._tcp_sock.connect((self.host, self.port))
            self._tcp_sock.sendall(frame + b"\n")
            return True
        except Exception:
            pass
        try:
            self._reset_tcp()
            self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_sock.settimeout(self.timeout)
            self._tcp_sock.connect((self.host, self.port))
            self._tcp_sock.sendall(frame + b"\n")
            return True
        except Exception:
            self._reset_tcp()
            return False

    def _reset_tcp(self):
        sock = getattr(self, "_tcp_sock", None)
        if sock:
            try: sock.close()
            except Exception: pass
        self._tcp_sock = None

    def __del__(self):
        self._reset_tcp()
