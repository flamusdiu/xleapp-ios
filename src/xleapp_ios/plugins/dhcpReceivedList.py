import plistlib

from xleapp import Artifact, Search, WebIcon


class DhcpReceivedList(Artifact):
    def __post_init__(self):
        self.name = "Recevied List"
        self.category = "DHCP"
        self.web_icon = WebIcon.SETTINGS

    @Search("**/private/var/db/dhcpclient/leases/en*")
    def process(self) -> None:
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                if key in [
                    "IPAddress",
                    "LeastLength",
                    "LeastStartDate",
                    "RouterHardwareAddress",
                    "RouterIPAddress",
                    "SSID",
                ]:
                    self.data.append((key, value))
