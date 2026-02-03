"""Maple provider helper.

Provides a simple function to run Maple expressions via the Maple Docker image
using a node-locked license mounted at runtime and a fixed MAC address to
stabilize the container HOSTID.

Environment variables:
- MAPLE_IMAGE: Docker image tag to run (e.g., "maple2025:2025.1").
- MAPLE_LICENSE_FILE: Absolute path on the host to activated license.dat.
- MAPLE_MAC: MAC address to pin for HOSTID stability
  (e.g., "02:42:ac:11:00:05").

Usage:
    from denario.providers import maple
    result = maple.run("evalf(Int(sin(x),x=0..1))")
"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import Optional


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} must be set")
    return value


def run(
    expr: str,
    mode: str = "plaintext",
    timeout_seconds: Optional[int] = 120,
) -> str:
    """Run a Maple expression inside the configured Docker image.

    Args:
        expr: Maple expression to evaluate
            (e.g., "evalf(Int(sin(x),x=0..1))").
        mode: "plaintext" or "latex".
            If "latex", wraps the expression with latex().
        timeout_seconds: Optional timeout for the docker run.

    Returns:
        Captured stdout from Maple (leading/trailing whitespace stripped).

    Raises:
        RuntimeError: If docker execution fails or returns a non-zero code.
    """

    image = _require_env("MAPLE_IMAGE")
    license_file = _require_env("MAPLE_LICENSE_FILE")
    mac_addr = _require_env("MAPLE_MAC")

    # Build Maple input program
    if mode.lower() == "latex":
        # Split across literals to keep line length within linter limits
        maple_code = (
            "interface(prettyprint=0): print(latex(" + expr + ")); quit;"
        )
    else:
        maple_code = f"interface(prettyprint=0): {expr}; quit;"

    # Compose docker command
    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "--mac-address",
        mac_addr,
        "-v",
        f"{license_file}:/opt/maple2025/license/license.dat:ro",
        image,
        "bash",
        "-lc",
        # Use single quotes around the echo program; escape inner quotes
        f"echo {shlex.quote(maple_code)} | maple -q",
    ]

    try:
        proc = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Maple docker run timed out after {timeout_seconds}s"
        ) from exc

    if proc.returncode != 0:
        raise RuntimeError(
            "Maple docker run failed\n"
            f"Command: {' '.join(docker_cmd)}\n"
            f"Exit: {proc.returncode}\nSTDERR:\n{proc.stderr}\n"
            f"STDOUT:\n{proc.stdout}"
        )

    return proc.stdout.strip()
