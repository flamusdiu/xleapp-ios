import plistlib

from xleapp import Artifact, Search, WebIcon
from xleapp.templating.html import NavigationItem


class CellularWirless(Artifact):
    def __post_init__(self) -> NavigationItem:
        self.name = "Celluar Wireless"
        self.category = "Celluar Wireless"
        self.description = "Celluar Wireless"
        self.web_icon = WebIcon.BAR_CHART
        self.report_headers = ("Key", "Value", "Source")

    @Search(
        "**/com.apple.commcenter.plist",
        "**/com.apple.commcenter.device_specific_nobackup.plist",
    )
    def process(self) -> None:
        device_info = self.app.device

        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                self.data.append((key, value))
                if key in (
                    "ReportedPhoneNumber",
                    "CDMANetworkPhoneNumberICCID",
                    "imei",
                    "LastKnownICCID",
                    "meid",
                ):
                    if key in ["imei", "meid"]:
                        key = key.upper()
                    device_info.update({key: value})
