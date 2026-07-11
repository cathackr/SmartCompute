"""
SmartCompute unified CLI.

Entry point registered as ``smartcompute`` console script.
Also accessible via ``python -m smartcompute``.

Subcommands
-----------
scan        Run an OSI layer analysis
monitor     Real-time process & resource monitoring
report      Generate an HTML report from the last scan
status      Show version and system info
serve       Start the FastAPI server
"""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    from smartcompute._version import __version__

    parser = argparse.ArgumentParser(
        prog="smartcompute",
        description="SmartCompute — Industrial Cybersecurity & Monitoring Platform",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"smartcompute {__version__}"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── scan ────────────────────────────────────────────────────
    scan_p = sub.add_parser("scan", help="Run OSI layer analysis")
    scan_p.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Analysis duration in seconds (default: 30)",
    )
    scan_p.add_argument(
        "--output", "-o", help="Output JSON path (default: auto-generated)"
    )

    # ── monitor ─────────────────────────────────────────────────
    mon_p = sub.add_parser("monitor", help="Real-time process monitoring")
    mon_p.add_argument(
        "--filter",
        nargs="*",
        default=["python", "node", "smartcompute"],
        help="Process name filters",
    )

    # ── report ──────────────────────────────────────────────────
    rep_p = sub.add_parser("report", help="Generate HTML report")
    rep_p.add_argument("json_path", help="Path to JSON scan results")
    rep_p.add_argument("--no-open", action="store_true", help="Don't auto-open in browser")

    # ── status ──────────────────────────────────────────────────
    sub.add_parser("status", help="Show version and system information")

    # ── serve ───────────────────────────────────────────────────
    srv_p = sub.add_parser("serve", help="Start FastAPI server")
    srv_p.add_argument("--host", default="0.0.0.0", help="Bind address")
    srv_p.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    srv_p.add_argument(
        "--workers", type=int, default=2, help="Uvicorn workers (default: 2)"
    )

    return parser


# ── Command handlers ────────────────────────────────────────────


def _cmd_scan(args: argparse.Namespace) -> None:
    from smartcompute.core.osi_analyzer import OSILayerAnalyzer
    import json

    analyzer = OSILayerAnalyzer()
    results = analyzer.analyze_all_layers(duration=args.duration)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2, default=str))


def _cmd_monitor(args: argparse.Namespace) -> None:
    import asyncio
    from smartcompute.core.monitor import SmartComputeProcessMonitor

    monitor = SmartComputeProcessMonitor()
    report = asyncio.run(monitor.generate_process_report(args.filter))
    path = monitor.save_report(report)
    print(f"Report saved to {path}")


def _cmd_report(args: argparse.Namespace) -> None:
    from smartcompute.core.reports import SmartComputeHTMLReportGenerator

    gen = SmartComputeHTMLReportGenerator()
    html_path = gen.generate_analysis_html(
        args.json_path, auto_open=not args.no_open
    )
    print(f"HTML report: {html_path}")


def _cmd_status(args: argparse.Namespace) -> None:
    import platform
    from smartcompute._version import __version__

    print(f"SmartCompute v{__version__} (OSS edition)")
    print(f"  Python:   {platform.python_version()}")
    print(f"  Platform: {platform.system()} {platform.release()}")


def _cmd_serve(args: argparse.Namespace) -> None:
    try:
        import uvicorn
    except ImportError:
        print(
            "uvicorn is required: pip install smartcompute[free]",
            file=sys.stderr,
        )
        sys.exit(1)

    uvicorn.run(
        "smartcompute.api.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
    )


_DISPATCH = {
    "scan": _cmd_scan,
    "monitor": _cmd_monitor,
    "report": _cmd_report,
    "status": _cmd_status,
    "serve": _cmd_serve,
}


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    handler = _DISPATCH.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)
