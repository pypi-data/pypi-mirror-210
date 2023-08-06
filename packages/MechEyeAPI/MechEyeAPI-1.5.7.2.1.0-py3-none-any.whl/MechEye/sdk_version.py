"""Get version information for the library."""
import _MechEye


class SDKVersion:  # pylint: disable=too-few-public-methods
    """Get the version of the loaded library."""

    major = _MechEye.version.major
    minor = _MechEye.version.minor
    patch = _MechEye.version.patch
    build = _MechEye.version.build
    full = _MechEye.version.full
