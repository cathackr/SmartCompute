"""Tests for the OSI layer analyzer (Starter tier)."""

from __future__ import annotations

import pytest

from smartcompute.core.osi_analyzer import OSILayerAnalyzer


class TestOSILayerAnalyzer:
    def test_creates_instance(self):
        analyzer = OSILayerAnalyzer()
        assert analyzer.system_info is not None
        assert "os" in analyzer.system_info
        assert "hostname" in analyzer.system_info

    def test_analyze_all_layers_returns_dict(self):
        analyzer = OSILayerAnalyzer()
        result = analyzer.analyze_all_layers(duration=1)

        assert isinstance(result, dict)
        assert "layers" in result
        assert "system_info" in result
        assert "timestamp" in result
