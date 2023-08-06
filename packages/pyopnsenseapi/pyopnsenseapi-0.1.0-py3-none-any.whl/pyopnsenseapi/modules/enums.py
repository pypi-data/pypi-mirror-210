"""OPNsense enums"""
from enum import Enum

class PackageManagerActions(Enum):
    """Valid pack_man actions"""
    INSTALL = "install"
    UNINSTALL = "remove"
    REINSTALL = "reinstall"
    LOCK = "lock"
    UNLOCK = "unlock"
    DETAILS = "details"
    LICENSE = "license"

class TracerDetail(Enum):
    """Valid tracer detail types."""
    NORMAL = "normal"

    def __str__(self) -> str:
        return self.value

class IpAddressTypes(Enum):
    """Valid IP types."""
    ANY = "any"
    IPV4 = "ip"
    IPV6 = "ip6"

    def __str__(self) -> str:
        return self.value

class CarpStatus(Enum):
    """Valid CARP status values"""
    ENABLE = "enable"
    DISABLE = "disable"
    MAINTENANCE = "maintenance"

    def __str__(self) -> str:
        return self.value
