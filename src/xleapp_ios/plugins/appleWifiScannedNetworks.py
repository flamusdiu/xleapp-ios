import logging
import plistlib

from xleapp import Artifact, Search, WebIcon

from ..helpers.utils import bytes_to_mac_address


class ScannedNetwork:
    ssid: str
    bssid: str
    added_at: str
    last_joined: str
    last_updated: str
    private_mac_in_use: str
    private_mac_value: str
    private_mac_valid: str
    in_known_networks: str
    last_auto_joined: str
    plist: str

    def __init__(self, network: dict) -> None:
        self.ssid = str(network.get("SSID_STR", ""))
        self.bssid = str(network.get("BSSID", ""))
        self.last_updated = str(network.get("lastUpdated", ""))
        self.last_joined = str(network.get("lastJoined", ""))
        self.added_at = str(network.get("addedAt", ""))
        self.in_known_networks = str(
            network.get(
                "PresentInKnownNetworks",
                "",
            ),
        )

        private_mac_address = network.get("PRIVATE_MAC_ADDRESS", "")
        if private_mac_address:
            self.private_mac_in_use = str(
                bytes_to_mac_address(
                    private_mac_address.get("PRIVATE_MAC_ADDRESS_IN_USE", ""),
                ),
            )
            self.private_mac_value = (
                str(
                    bytes_to_mac_address(
                        private_mac_address.get("PRIVATE_MAC_ADDRESS_VALUE", ""),
                    ),
                ),
            )
            self.private_mac_valid = (
                str(
                    private_mac_address.get("PRIVATE_MAC_ADDRESS_VALID", ""),
                ),
            )

    def attributes(self) -> list[str]:
        return [val for _, val in self.__dict__.items()]


class AppleWifiScannedPrivate(Artifact):
    def __post_init__(self):
        self.name = "Wifi Networks Scanned (private)"
        self.description = 'WiFi networks scanned while using fake ("private") MAC address. Dates are taken straight from the source plist.'
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

    @Search(
        "**/com.apple.wifi.plist",
        "**/com.apple.wifi-networks.plist.backup",
        "**/com.apple.wifi.known-networks.plist",
        "**/com.apple.wifi-private-mac-networks.plist",
    )
    def process(self):
        for fp in self.found:
            deserialzied = plistlib.load(fp(), fmt=plistlib.FMT_BINARY)

            scanned_networks = []
            try:
                for scanned_network in deserialzied[
                    "List of scanned networks with private mac"
                ]:
                    network = ScannedNetwork(scanned_network)
                    network.plist = fp().name
                    scanned_networks.append(network.attributes())
            except KeyError:
                self.log(logging.INFO, "-> No private networks scanned in plist file.")

        self.data = scanned_networks
