"""OPNsense enums"""
from enum import Enum

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
