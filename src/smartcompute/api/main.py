"""
SmartCompute FastAPI application.

Provides REST endpoints for monitoring, license activation,
and webhook handling.

Run with::

    smartcompute serve
    # or
    uvicorn smartcompute.api.main:app --host 0.0.0.0 --port 5000
"""

from __future__ import annotations

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
except ImportError:
    raise ImportError(
        "FastAPI is required for the API server. "
        "Install with: pip install smartcompute[enterprise]"
    )

from smartcompute._version import __version__

app = FastAPI(
    title="SmartCompute API",
    version=__version__,
    description="Industrial Cybersecurity & Monitoring Platform",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and Docker."""
    return {"status": "healthy", "version": __version__}


@app.get("/api/status")
async def api_status():
    """Return current system and license status."""
    from smartcompute.licensing.validator import LicenseValidator

    validator = LicenseValidator()
    info = validator.get_current_license()
    return {
        "version": __version__,
        "tier": info.tier,
        "org": info.org,
        "valid": info.valid,
    }


@app.post("/api/activate")
async def activate_license(payload: dict):
    """Activate a license token."""
    token = payload.get("token", "")
    if not token:
        raise HTTPException(status_code=400, detail="Missing 'token' field")

    from smartcompute.licensing.validator import LicenseValidator

    validator = LicenseValidator()
    info = validator.activate(token)

    if not info.valid:
        raise HTTPException(status_code=400, detail=info.error)

    return {
        "status": "activated",
        "tier": info.tier,
        "org": info.org,
        "expires_at": info.expires_at,
    }


@app.post("/api/webhook/mercadopago")
async def mercadopago_webhook(payload: dict):
    """Receive MercadoPago payment notifications.

    In production, this should verify the webhook signature
    and trigger license generation.
    """
    # TODO: Implement signature verification and auto-license generation
    return {"status": "received"}
