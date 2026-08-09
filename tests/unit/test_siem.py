"""Tests for the SIEM integrations (Wazuh connector, CEF formatter, SIEMManager)."""

import json

import pytest

from smartcompute.industrial.siem import (
    SIEMManager,
    SmartComputeCEFFormatter,
    WazuhConnector,
)
from smartcompute.industrial.siem.wazuh_connector import _risk_to_sev, _FAC_LOCAL0


class TestRiskToSeverity:
    def test_critical(self):
        assert _risk_to_sev(0.95) == 2

    def test_error(self):
        assert _risk_to_sev(0.75) == 3

    def test_warning(self):
        assert _risk_to_sev(0.55) == 4

    def test_notice(self):
        assert _risk_to_sev(0.1) == 5

    def test_boundaries(self):
        assert _risk_to_sev(0.90) == 2
        assert _risk_to_sev(0.70) == 3
        assert _risk_to_sev(0.50) == 4


class TestWazuhFrame:
    def test_frame_is_valid_syslog_with_json_body(self):
        conn = WazuhConnector(host="127.0.0.1")
        payload = {"anomaly_type": "ot_modbus_write", "risk_score": 0.8, "source_host": "plc-01"}
        frame = conn._build_frame(payload, severity=3).decode("utf-8")

        # PRI = facility*8 + severity
        assert frame.startswith(f"<{_FAC_LOCAL0 * 8 + 3}>")
        # program_name que matchea el decoder de Wazuh
        assert " smartcompute smartcompute: " in frame
        # el cuerpo debe ser JSON parseable (JSON_Decoder)
        body = frame.split("smartcompute: ", 1)[1]
        assert json.loads(body) == payload

    def test_send_anomaly_event_reports_destination(self, monkeypatch):
        conn = WazuhConnector(host="127.0.0.1", port=5514, protocol="udp")
        sent = {}
        monkeypatch.setattr(conn, "_send_udp", lambda frame: sent.setdefault("frame", frame) or True)

        result = conn.send_anomaly_event({"anomaly_type": "test", "risk_score": 0.95})

        assert result["status"] == "success"
        assert result["destination"] == "127.0.0.1:5514/udp"
        assert b'"anomaly_type"' in sent["frame"]

    def test_emit_failure_returns_error_status(self, monkeypatch):
        conn = WazuhConnector(host="127.0.0.1")
        monkeypatch.setattr(conn, "_send_udp", lambda frame: (_ for _ in ()).throw(OSError("boom")))

        result = conn.send_anomaly_event({"risk_score": 0.9})
        assert result["status"] == "error"


class TestCEFFormatter:
    def test_anomaly_event_header_and_fields(self):
        fmt = SmartComputeCEFFormatter()
        event = fmt.format_anomaly_event(
            {
                "anomaly_type": "cpu_spike",
                "source_host": "web-01",
                "risk_score": 0.85,
                "cpu_usage": 95.5,
                "description": "spike",
            }
        )
        assert event.startswith("CEF:0|SmartCompute|PerformanceMonitor|")
        assert "|SC_CPU_SPIKE|" in event
        assert "|8|" in event  # risk 0.85 → HIGH
        assert "dhost=web-01" in event
        assert "cs4=0.85" in event

    def test_severity_mapping(self):
        fmt = SmartComputeCEFFormatter()
        assert "|10|" in fmt.format_anomaly_event({"risk_score": 0.95})
        assert "|5|" in fmt.format_anomaly_event({"risk_score": 0.5})
        assert "|0|" in fmt.format_anomaly_event({"risk_score": 0.1})


class TestSIEMManager:
    def test_defaults_without_config_file(self, tmp_path):
        mgr = SIEMManager(config_path=str(tmp_path / "missing.yaml"))
        assert mgr.connectors == {}
        status = mgr.get_status()
        assert status["enabled_connectors"] == []
        assert status["min_risk_score"] == 0.3

    def test_event_below_threshold_is_skipped(self, tmp_path):
        mgr = SIEMManager(config_path=str(tmp_path / "missing.yaml"))
        result = mgr.send_anomaly({"anomaly_type": "low", "risk_score": 0.1})
        assert "skipped" in result

    def test_wazuh_connector_from_yaml_config(self, tmp_path, monkeypatch):
        yaml = pytest.importorskip("yaml")
        cfg = tmp_path / "siem_config.yaml"
        cfg.write_text(
            "siem_settings:\n  min_risk_score: 0.3\n"
            "wazuh:\n  enabled: true\n  host: 127.0.0.1\n  port: 5514\n  protocol: udp\n"
        )
        mgr = SIEMManager(config_path=str(cfg))
        assert list(mgr.connectors.keys()) == ["wazuh"]

        monkeypatch.setattr(mgr.connectors["wazuh"], "_send_udp", lambda frame: True)
        result = mgr.send_anomaly({"anomaly_type": "ot_test", "risk_score": 0.9})
        assert result["wazuh"][0]["status"] == "success"
