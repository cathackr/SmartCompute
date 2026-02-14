"""
Tests for SmartCompute core monitoring (Starter tier).

Covers: process monitoring, system resources, network overview.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch, MagicMock

import psutil
import pytest

from smartcompute.core.monitor import (
    SmartComputeProcessMonitor,
    ProcessInfo,
    NetworkConnection,
)


class TestProcessMonitorInit:
    def test_creates_instance(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor.monitoring is False
        assert isinstance(monitor.network_interfaces, dict)

    def test_detects_network_interfaces(self):
        monitor = SmartComputeProcessMonitor()
        # Should have at least loopback
        assert len(monitor.network_interfaces) >= 1


class TestAdapterTypeDetection:
    def test_ethernet(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("eth0") == "Ethernet"
        assert monitor._detect_adapter_type("enp3s0") == "Ethernet"

    def test_wifi(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("wlan0") == "WiFi/Wireless"
        assert monitor._detect_adapter_type("wlp2s0") == "WiFi/Wireless"

    def test_loopback(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("lo") == "Loopback"

    def test_vpn(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("tun0") == "VPN/Tunnel"

    def test_docker(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("docker0") == "Container/Virtual"

    def test_unknown(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_adapter_type("xyz999") == "Other/Unknown"


class TestCableCategoryDetection:
    def test_10gbps(self):
        monitor = SmartComputeProcessMonitor()
        assert "6A" in monitor._detect_cable_category("eth0", 10000) or \
               "7" in monitor._detect_cable_category("eth0", 10000)

    def test_1gbps(self):
        monitor = SmartComputeProcessMonitor()
        result = monitor._detect_cable_category("eth0", 1000)
        assert "5e" in result or "6" in result

    def test_wireless(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_cable_category("wlan0", 0) == "Wireless"

    def test_virtual(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._detect_cable_category("lo", 0) == "Virtual"


class TestMacManufacturer:
    def test_known_vendor(self):
        monitor = SmartComputeProcessMonitor()
        assert "VMware" in monitor._get_mac_manufacturer("00:50:56:aa:bb:cc")

    def test_unknown_vendor(self):
        monitor = SmartComputeProcessMonitor()
        assert "Unknown" in monitor._get_mac_manufacturer("ff:ff:ff:ff:ff:ff")

    def test_empty_mac(self):
        monitor = SmartComputeProcessMonitor()
        assert monitor._get_mac_manufacturer("") == "Unknown"
        assert monitor._get_mac_manufacturer("N/A") == "Unknown"


class TestSystemResources:
    @pytest.mark.asyncio
    async def test_get_system_resources(self):
        monitor = SmartComputeProcessMonitor()
        resources = await monitor.get_system_resources_detailed()

        assert "cpu" in resources
        assert "memory" in resources
        assert "disk" in resources
        assert "network" in resources
        assert "timestamp" in resources

    @pytest.mark.asyncio
    async def test_cpu_info(self):
        monitor = SmartComputeProcessMonitor()
        resources = await monitor.get_system_resources_detailed()

        cpu = resources["cpu"]
        assert "percent" in cpu
        assert "count_logical" in cpu
        assert cpu["count_logical"] >= 1

    @pytest.mark.asyncio
    async def test_memory_info(self):
        monitor = SmartComputeProcessMonitor()
        resources = await monitor.get_system_resources_detailed()

        mem = resources["memory"]
        assert "total_gb" in mem
        assert mem["total_gb"] > 0


class TestProcessReport:
    @pytest.mark.asyncio
    async def test_generate_report(self):
        monitor = SmartComputeProcessMonitor()
        report = await monitor.generate_process_report(["python"])

        assert "summary" in report
        assert "processes" in report
        assert "system_resources" in report
        assert "timestamp" in report
        assert report["summary"]["total_processes"] > 0

    @pytest.mark.asyncio
    async def test_report_contains_network(self):
        monitor = SmartComputeProcessMonitor()
        report = await monitor.generate_process_report(["python"])

        assert "network_connections" in report
        assert "listening_ports" in report


class TestProcessInfoDataclass:
    def test_fields(self):
        info = ProcessInfo(
            pid=1,
            name="test",
            cmdline=["test"],
            exe="/usr/bin/test",
            cwd="/tmp",
            cpu_percent=1.0,
            memory_percent=0.5,
            memory_mb=100,
            status="running",
            create_time=0.0,
            num_threads=1,
            connections=[],
            open_files=[],
            environment={},
            parent_pid=0,
            username="root",
        )
        assert info.pid == 1
        assert info.name == "test"
