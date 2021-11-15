from xleapp import Artifact, Search, WebIcon


class DhcpHotspotClients(Artifact):
    def __post_init__(self) -> None:
        self.name = "Hotspot Clients"
        self.category = "DHCP"
        self.report_headers = ("Hotspot Clients",)
        self.web_icon = WebIcon.SETTINGS

    @Search("**/private/var/db/dhcpd_leases*")
    def process(self) -> None:
        for fp in self.found:
            for line in fp():
                cline = line.strip()
                if cline not in ["{", "}"]:
                    ll = cline.split("=")
                    self.data.append(ll)
