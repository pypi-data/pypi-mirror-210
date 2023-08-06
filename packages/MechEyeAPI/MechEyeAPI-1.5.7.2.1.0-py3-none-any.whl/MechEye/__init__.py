"""This file imports all non protected classes, modules and packages from the current level."""
import MechEye._version
__version__ = MechEye._version.get_version(__name__)  # pylint: disable=protected-access


from MechEye.device import Device