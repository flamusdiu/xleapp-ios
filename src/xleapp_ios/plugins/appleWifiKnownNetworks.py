import logging
import plistlib

from xleapp import Artifact, Search, WebIcon


class AppleWifiKnownNetworks(Artifact):
    def __post_init__(self):
        self.name = "Wifi Known Networks"
        self.description = (
            "WiFi known networks data. Dates are taken straight from the source plist."
        )
        self.category = "Locations"
        self.report_headers = (
            "SSID",
            "BSSID",
            "Network Usage",
            "Country Code",
            "Device Name",
            "Manufacturer",
            "Serial Number",
            "Model Name",
            "Last Joined",
            "Last Auto Joined",
            "Last Updated",
            "Enabled",
            "WiFi Network Password Modification Date",
            "File",
        )
        self.report_title = "WiFi Known Networks"
        self.web_icon = WebIcon.WIFI

    @Search(
        "**/com.apple.wifi.plist",
        "**/com.apple.wifi-networks.plist.backup",
        "**/com.apple.wifi.known-networks.plist",
        "**/com.apple.wifi-private-mac-networks.plist",
    )
    def process(self):
        class KnownNetwork:
            ssid: str
            bssid: str
            net_usage: str
            country_code: str
            device_name: str = ""
            manufacturer: str = ""
            serial_number: str = ""
            model_name: str = ""
            last_joined: str
            last_updated: str
            last_auto_joined: str
            enabled: str
            wnpmd: str
            plist: str

            def __init__(self, network: dict) -> None:

                self.ssid = str(network.get("SSID_STR", ""))
                self.bssid = str(network.get("BSSID", ""))
                self.net_usage = str(network.get("networkUsage", ""))
                self.country_code = str(
                    network.get("80211D_IE", {}).get("IE_KEY_80211D_COUNTRY_CODE", ""),
                )
                self.last_updated = str(network.get("lastUpdated", ""))
                self.last_joined = str(network.get("lastJoined", ""))
                self.last_auto_joined = str(network.get("lastAutoJoined", ""))
                self.wnpmd = str(
                    network.get("WiFiNetworkPasswordModificationDate", ""),
                )
                self.enabled = network.get("enabled", "")

                wps_prob_resp_ie = network.get("WPS_PROB_RESP_IE", "")
                if wps_prob_resp_ie:
                    self.device_name = wps_prob_resp_ie.get("IE_KEY_WPS_DEV_NAME", "")
                    self.manufacturer = wps_prob_resp_ie.get(
                        "IE_KEY_WPS_MANUFACTURER", ""
                    )
                    self.serial_number = wps_prob_resp_ie.get("IE_KEY_WPS_SERIAL_NUM", "")
                    self.model_name = wps_prob_resp_ie.get(
                        "IE_KEY_WPS_MODEL_NAME",
                        "",
                    )

            def attributes(self) -> list[str]:
                return [
                    self.ssid,
                    self.bssid,
                    self.net_usage,
                    self.country_code,
                    self.device_name,
                    self.manufacturer,
                    self.serial_number,
                    self.model_name,
                    self.last_joined,
                    self.last_updated,
                    self.last_auto_joined,
                    self.enabled,
                    self.wnpmd,
                    self.plist,
                ]

        for fp in self.found:
            deserialized = plistlib.load(fp())

            known_networks = []
            try:
                for known_network in deserialized["List of known networks"]:
                    network = KnownNetwork(known_network)
                    network.plist = fp().name
                    known_networks.append(network.attributes())
            except KeyError:
                self.log(logging.INFO, "-> No networks found in plist.")

        self.data = known_networks
