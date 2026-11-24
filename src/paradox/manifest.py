# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
"""Run manifest: config hash, seeds, git revision, versions, OS, CPU, runtime
and peak memory (master prompt section 4)."""

from __future__ import annotations

import platform
import resource
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

from . import __version__

__all__ = ["git_revision", "environment", "peak_rss_bytes", "utc_now", "build_manifest"]

_PACKAGES = ("numpy", "matplotlib", "jsonschema", "typst", "pytest", "hypothesis")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_revision(repo: Path | None = None) -> str:
    """``<sha>`` or ``<sha>-dirty``; ``unknown`` if git is unavailable."""
    cwd = str(repo or Path(__file__).resolve().parents[2])
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return f"{sha}-dirty" if dirty else sha


def _cpu() -> str:
    if sys.platform == "darwin":
        try:
            return subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return platform.processor() or platform.machine()


def environment() -> dict:
    versions = {"paradox": __version__, "python": platform.python_version()}
    for name in _PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return {"os": f"{platform.system()} {platform.release()} ({platform.platform()})", "machine": platform.machine(), "cpu": _cpu(), "versions": versions}


def peak_rss_bytes() -> int:
    """Peak resident set size of this process (macOS reports bytes, Linux KiB)."""
    v = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(v if sys.platform == "darwin" else v * 1024)


def build_manifest(*, experiment_id: str, label: str, config_sha256: str, seeds: list[int], command: list[str],
                   started_utc: str, finished_utc: str, runtime_s: float, per_record_runtime_s: dict, outputs: dict) -> dict:
    return {
        "manifest_version": "1.0.0",
        "experiment_id": experiment_id,
        "label": label,
        "config_sha256": config_sha256,
        "seeds": seeds,
        "git_revision": git_revision(),
        "command": command,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "runtime_s": runtime_s,
        "per_record_runtime_s": per_record_runtime_s,
        "peak_rss_bytes": peak_rss_bytes(),
        "peak_rss_note": "process-level peak resident set size from getrusage, includes interpreter and imports",
        "environment": environment(),
        "outputs": outputs,
    }
