import datetime
import plistlib

from xleapp import Artifact, Search, core_artifact


@core_artifact
class LastBuild(Artifact):
    def __post_init__(self):
        self.name = "Last Build"
        self.category = "IOS Build"

    @Search("*LastBuildInfo.plist")
    def process(self):
        data_list = []
        device_info = self.app.device
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                data_list.append((key, value))
                if key in ["ProductVersion", "ProductBuildVersion", "ProductName"]:
                    device_info.update({key: value})
        self.data = data_list


@core_artifact
class ItunesBackupInfo(Artifact):
    def __post_init__(self):
        self.name = "iTunes Backup"
        self.category = "IOS Build"

    @Search("Info.plist")
    def process(self):
        data_list = []
        device_info = self.app.device
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                if (
                    isinstance(value, str)
                    or isinstance(value, int)
                    or isinstance(value, datetime.datetime)
                ):

                    data_list.append((key, value))
                    if key in (
                        "Build Version",
                        "Device Name",
                        "ICCID",
                        "IMEI",
                        "Last Backup Date",
                        "MEID",
                        "Phone Number",
                        "Product Name",
                        "Product Type",
                        "Product Version",
                        "Serial Number",
                    ):
                        device_info.update({key: value})

                elif key == "Installed Applications":
                    data_list.append((key, ", ".join(value)))
        self.data = data_list
