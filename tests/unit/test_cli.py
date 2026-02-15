"""Tests for the SmartCompute CLI."""

from __future__ import annotations

import pytest

from smartcompute._version import __version__
from smartcompute.cli import main, _build_parser


class TestCLIParser:
    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert __version__ in captured.out

    def test_no_args_shows_help(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 0

    def test_parser_has_all_subcommands(self):
        parser = _build_parser()
        # Parse each subcommand to verify it exists
        for cmd in ["scan", "monitor", "status"]:
            args = parser.parse_args([cmd])
            assert args.command == cmd

    def test_activate_requires_token(self):
        parser = _build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["activate"])  # missing required token arg

    def test_scan_default_duration(self):
        parser = _build_parser()
        args = parser.parse_args(["scan"])
        assert args.duration == 30

    def test_serve_defaults(self):
        parser = _build_parser()
        args = parser.parse_args(["serve"])
        assert args.host == "0.0.0.0"
        assert args.port == 5000
        assert args.workers == 2
