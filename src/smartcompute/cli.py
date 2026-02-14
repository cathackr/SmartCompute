"""
SmartCompute unified CLI.

Entry point registered as ``smartcompute`` console script.
Also accessible via ``python -m smartcompute``.

Subcommands
-----------
scan        Run an OSI layer analysis
monitor     Real-time process & resource monitoring
report      Generate an HTML report from the last scan
activate    Activate a license token
status      Show current license and system info
serve       Start the FastAPI server
enterprise  Run enterprise-tier features
industrial  Run industrial-tier features
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

    # ── activate ────────────────────────────────────────────────
    act_p = sub.add_parser("activate", help="Activate a license token")
    act_p.add_argument("token", help="License token string")

    # ── status ──────────────────────────────────────────────────
    sub.add_parser("status", help="Show license and system information")

    # ── serve ───────────────────────────────────────────────────
    srv_p = sub.add_parser("serve", help="Start FastAPI server")
    srv_p.add_argument("--host", default="0.0.0.0", help="Bind address")
    srv_p.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    srv_p.add_argument(
        "--workers", type=int, default=2, help="Uvicorn workers (default: 2)"
    )

    # ── enterprise ──────────────────────────────────────────────
    ent_p = sub.add_parser("enterprise", help="Enterprise-tier features")
    ent_p.add_argument(
        "feature",
        nargs="?",
        choices=["xdr", "siem", "ml", "mcp"],
        help="Feature to run",
    )

    # ── industrial ──────────────────────────────────────────────
    ind_p = sub.add_parser("industrial", help="Industrial-tier features")
    ind_p.add_argument(
        "feature",
        nargs="?",
        choices=["protocols", "scada", "compliance", "variables"],
        help="Feature to run",
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
    html_path = gen.generate_enterprise_analysis_html(
        args.json_path, auto_open=not args.no_open
    )
    print(f"HTML report: {html_path}")


def _cmd_activate(args: argparse.Namespace) -> None:
    from smartcompute.licensing.validator import LicenseValidator

    validator = LicenseValidator()
    info = validator.activate(args.token)

    if info.valid:
        print(f"License activated successfully!")
        print(f"  Tier:  {info.tier}")
        print(f"  Org:   {info.org}")
        print(f"  Email: {info.email}")
        print(f"  Expires: {info.expires_at}")
    else:
        print(f"Activation failed: {info.error}", file=sys.stderr)
        sys.exit(1)


def _cmd_status(args: argparse.Namespace) -> None:
    from smartcompute._version import __version__
    from smartcompute.licensing.validator import LicenseValidator
    from smartcompute.licensing.hardware_id import get_hardware_id

    validator = LicenseValidator()
    info = validator.get_current_license()

    print(f"SmartCompute v{__version__}")
    print(f"  Hardware ID: {get_hardware_id()}")
    print(f"  License:     {info.tier.upper()}")
    if info.tier != "starter":
        print(f"  Org:         {info.org}")
        print(f"  Expires:     {info.expires_at}")
    else:
        print("  (Free tier — upgrade at https://github.com/cathackr/smartcompute#pricing)")


def _cmd_serve(args: argparse.Namespace) -> None:
    try:
        import uvicorn
    except ImportError:
        print(
            "uvicorn is required: pip install smartcompute[enterprise]",
            file=sys.stderr,
        )
        sys.exit(1)

    uvicorn.run(
        "smartcompute.api.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
    )


def _cmd_enterprise(args: argparse.Namespace) -> None:
    from smartcompute.licensing.decorators import requires_tier, TierRequiredError

    try:
        _check = requires_tier("enterprise")(lambda: None)
        _check()
    except TierRequiredError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if not args.feature:
        print("Enterprise features: xdr, siem, ml, mcp")
        print("Usage: smartcompute enterprise <feature>")
        return

    print(f"Running enterprise/{args.feature} ...")
    # Feature dispatch would go here; for now, confirm access.
    print(f"Enterprise feature '{args.feature}' is available with your license.")


def _cmd_industrial(args: argparse.Namespace) -> None:
    from smartcompute.licensing.decorators import requires_tier, TierRequiredError

    try:
        _check = requires_tier("industrial")(lambda: None)
        _check()
    except TierRequiredError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    if not args.feature:
        print("Industrial features: protocols, scada, compliance, variables")
        print("Usage: smartcompute industrial <feature>")
        return

    print(f"Running industrial/{args.feature} ...")
    print(f"Industrial feature '{args.feature}' is available with your license.")


_DISPATCH = {
    "scan": _cmd_scan,
    "monitor": _cmd_monitor,
    "report": _cmd_report,
    "activate": _cmd_activate,
    "status": _cmd_status,
    "serve": _cmd_serve,
    "enterprise": _cmd_enterprise,
    "industrial": _cmd_industrial,
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
