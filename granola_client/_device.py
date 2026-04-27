"""Helpers that mirror what the Granola Electron app puts in API request headers.

The live desktop app builds X-Granola-Device-Id, X-Granola-Platform and
X-Granola-Os-Version from local system calls (ioreg / sw_vers / Windows registry)
and sends them on every api.granola.ai request. The server now gates on this
identity, so the Python client has to compute the same values.
"""

import hashlib
import logging
import platform
import plistlib
import re
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


_PLATFORM_LABELS = {"Darwin": "macOS", "Windows": "Windows"}


def get_platform_label(system: Optional[str] = None) -> str:
    """Return the X-Granola-Platform value for the current OS (or a given one).

    Granola uses 'macOS' / 'Windows' / 'web'. We don't run in a browser, so we map
    Darwin → macOS and Windows → Windows. Anything else falls back to the raw
    system name; the server will reject it, but that's the honest answer.
    """
    sys_name = system or platform.system()
    return _PLATFORM_LABELS.get(sys_name, sys_name)


def get_os_version() -> str:
    """Return the OS version string the desktop app would send.

    macOS uses `sw_vers -productVersion` (e.g. '15.0'). Windows uses platform.win32_ver.
    """
    sys_name = platform.system()
    if sys_name == "Darwin":
        try:
            out = subprocess.run(
                ["sw_vers", "-productVersion"],
                capture_output=True, text=True, check=True, timeout=5,
            ).stdout.strip()
            if out:
                return out
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug("sw_vers failed, falling back to platform.mac_ver: %s", e)
        return platform.mac_ver()[0] or ""
    if sys_name == "Windows":
        return platform.win32_ver()[0] or ""
    return platform.release()


def _read_macos_platform_uuid() -> Optional[str]:
    try:
        out = subprocess.run(
            ["ioreg", "-d2", "-c", "IOPlatformExpertDevice"],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout
    except (subprocess.SubprocessError, OSError) as e:
        logger.debug("ioreg failed: %s", e)
        return None
    for line in out.splitlines():
        if "IOPlatformUUID" not in line:
            continue
        # Format: '    "IOPlatformUUID" = "ABC-...-XYZ"'
        parts = line.split('"')
        for i, p in enumerate(parts):
            if p == "IOPlatformUUID" and i + 2 < len(parts):
                return parts[i + 2]
    return None


_WIN_GUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE)


def _read_windows_machine_guid() -> Optional[str]:
    try:
        out = subprocess.run(
            ["reg.exe", "query", r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
             "/v", "MachineGuid", "/reg:64"],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout
    except (subprocess.SubprocessError, OSError) as e:
        logger.debug("reg.exe query failed: %s", e)
        return None
    m = _WIN_GUID_RE.search(out)
    return m.group(0) if m else None


def get_hashed_device_id() -> Optional[str]:
    """Return sha256 hex of the platform device UUID, matching the Electron app.

    Returns None on platforms where we can't read a stable identifier — the header
    is then omitted, mirroring the desktop app's own behaviour when the lookup fails.
    """
    sys_name = platform.system()
    if sys_name == "Darwin":
        raw = _read_macos_platform_uuid()
    elif sys_name == "Windows":
        raw = _read_windows_machine_guid()
    else:
        raw = None
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_installed_granola_version() -> Optional[str]:
    """Read the locally-installed Granola.app version, if present.

    Lets the client track whatever Electron build is installed instead of going
    stale against every Granola release. Returns None if the app isn't found or
    the plist can't be parsed.
    """
    sys_name = platform.system()
    if sys_name == "Darwin":
        plist_path = Path("/Applications/Granola.app/Contents/Info.plist")
        if not plist_path.exists():
            return None
        try:
            with plist_path.open("rb") as f:
                data = plistlib.load(f)
        except (OSError, plistlib.InvalidFileException) as e:
            logger.debug("Failed to read Granola Info.plist: %s", e)
            return None
        version = data.get("CFBundleShortVersionString")
        return version if isinstance(version, str) else None
    return None
