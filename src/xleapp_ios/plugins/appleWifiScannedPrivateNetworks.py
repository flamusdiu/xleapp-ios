import logging
import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get

from ..helpers.utils import bytes_to_mac_address


class AppleWifiScannedPrivateNetworks(Artifact):
    def __post_init__(self) -> None:
        self.name = "Wifi Networks Scanned (private)"
        self.description = (
            "WiFi networks scanned while using fake ('private') MAC address. Dates "
            "are taken straight from the source plist."
        )
        self.category = "Locations"
        self.report_headers = (
            "SSID",
            "BSSID",
            "Added At",
            "Last Joined",
            "Last Updated",
            "MAC Used For Network",
            "Private MAC Computed For Network",
            "MAC Valid",
            "In Known Networks",
            "File",
        )
        self.report_title = "Wifi Networks Scanned (private)"
        self.web_icon = WebIcon.WIFI
        self.timeline = True

    @Search(
        "**/com.apple.wifi.plist",
        "**/com.apple.wifi-networks.plist.backup",
        "**/com.apple.wifi.known-networks.plist",
        "**/com.apple.wifi-private-mac-networks.plist",
    )
    def process(self):
        class ScannedNetwork:
            ssid: str
            bssid: str
            added_at: str
            last_joined: str
            last_updated: str
            private_mac_in_use: str = ""
            private_mac_value: str = ""
            private_mac_valid: str = ""
            in_known_networks: str
            last_auto_joined: str
            plist: str

            def __init__(self, network: dict) -> None:
                self.ssid = str(deep_get(network, "SSID_STR"))
                self.bssid = str(deep_get(network, "BSSID"))
                self.last_updated = str(deep_get(network, "lastUpdated"))
                self.last_joined = str(deep_get(network, "lastJoined"))
                self.added_at = str(deep_get("addedAt"))
                self.in_known_networks = str(deep_get(network, "PresentInKnownNetworks"))
                if network.get("PRIVATE_MAC_ADDRESS", ""):
                    self.private_mac_in_use = str(
                        bytes_to_mac_address(
                            deep_get(
                                network,
                                "PRIVATE_MAC_ADDRESS",
                                "PRIVATE_MAC_ADDRESS_IN_USE",
                            ),
                        ),
                    )
                    self.private_mac_value = (
                        str(
                            bytes_to_mac_address(
                                deep_get(
                                    network,
                                    "PRIVATE_MAC_ADDRESS",
                                    "PRIVATE_MAC_ADDRESS_VALUE",
                                ),
                            ),
                        ),
                    )
                    self.private_mac_valid = (
                        str(
                            deep_get(
                                network,
                                "PRIVATE_MAC_ADDRESS",
                                "PRIVATE_MAC_ADDRESS_VALID",
                            ),
                        ),
                    )

            def attributes(self) -> tuple[str]:
                return (
                    self.ssid,
                    self.bssid,
                    self.added_at,
                    self.last_joined,
                    self.last_updated,
                    self.private_mac_in_use,
                    self.private_mac_value,
                    self.private_mac_valid,
                    self.in_known_networks,
                    self.last_auto_joined,
                    self.plist,
                )

        for fp in self.found:
            deserialzied = plistlib.load(fp(), fmt=plistlib.FMT_BINARY)

            try:
                for scanned_network in deserialzied[
                    "List of scanned networks with private mac"
                ]:
                    network = ScannedNetwork(scanned_network)
                    network.plist = fp().name
                    self.data.append(network.attributes())
            except KeyError:
                self.log(logging.INFO, "-> No private networks scanned in plist file.")
