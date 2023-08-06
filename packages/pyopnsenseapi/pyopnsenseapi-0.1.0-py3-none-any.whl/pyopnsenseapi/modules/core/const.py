"""firmware module const"""

CORE = "core"

FUNCTIONS = {
    "FIRMWARE_POWER_OFF": "firmware.poweroff",
    "FIRMWARE_REBOOT": "firmware.reboot",
    "FIRMWARE_RUNNING": "firmware.running",
    "FIRMWARE_GET_FIRMWARE_CONFIG": "firmware.getFirmwareConfig",
    "FIRMWARE_GET_FIRMWARE_OPTIONS": "firmware.getFirmwareOptions",
    "FIRMWARE_SET_FIRMWARE_CONFIG": "firmware.setFirmwareConfig",
    "FIRMWARE_INFO": "firmware.info",
    "FIRMWARE_STATUS": "firmware.status",
    "FIRMWARE_AUDIT": "firmware.audit",
    "FIRMWARE_UPDATE": "firmware.update",
    "FIRMWARE_UPGRADE": "firmware.upgrade",
    "FIRMWARE_UPGRADE_STATUS": "firmware.upgradestatus",
    "FIRMWARE_CHANGELOG": "firmware.changelog?$version=%s",
    "FIRMWARE_INSTALL": "firmware.install?$pkg_name=%s",
    "FIRMWARE_REINSTALL": "firmware.reinstall?$pkg_name=%s",
    "FIRMWARE_REMOVE": "firmware.remove?$pkg_name=%s",
    "FIRMWARE_LOCK": "firmware.lock?$pkg_name=%s",
    "FIRMWARE_UNLOCK": "firmware.unlock?$pkg_name=%s",
    "FIRMWARE_DETAILS": "firmware.details?$pkg_name=%s",
    "FIRMWARE_LICENSE": "firmware.license?$pkg_name=%s",
    "SERVICE_RESTART": "service.restart?$name=%s&$id=%s",
    "SERVICE_SEARCH": "service.search",
    "SERVICE_START": "service.start?$name=%s&$id=%s",
    "SERVICE_STOP": "service.stop?$name=%s&$id=%s",
    "SYSTEM_DISMISS_STATUS": "system.dismissStatus",
    "SYSTEM_HALT": "system.halt",
    "SYSTEM_REBOOT": "system.reboot",
    "SYSTEM_STATUS": "system.status"
}

# Dynamic build endpoints
ENDPOINTS = {}
for v in FUNCTIONS.items():
    ENDPOINTS[str(v[1])] = f"{CORE}/{str(v[1]).replace('.', '/')}"
