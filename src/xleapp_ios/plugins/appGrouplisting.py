import pathlib
import plistlib
import sys
from dataclasses import dataclass

import biplist
from xleapp import Artifact, WebIcon, Search, timed


@dataclass
class AppGroupListing(Artifact):
    def __post_init__(self):
        self.name = "App Group Listing"
        self.description = (
            "List can included once installed but not present "
            "apps. Each file is named .com.apple.mobile_"
            "container_manager.metadata.plist"
        )
        self.category = "Installed Apps"
        self.report_headers = ("Bundle ID", "Type", "Directory GUID", "Path")
        self.report_title = "Bundle ID by AppGroup & PluginKit IDs"
        self.web_icon = WebIcon.PACKAGE

    @timed
    @Search(
        "*/private/var/mobile/Containers/Shared/AppGroup/*/*.metadata.plist",
        "**/PluginKitPlugin/*.metadata.plist",
    )
    def process(self):
        data_list = []

        for fp in self.found:
            plist = plistlib.load(fp())
            bundleid = plist["MCMMetadataIdentifier"]

            path = fp.path
            appgroupid = path.parent.name
            fileloc = path.parent
            typedir = path.parents[1].name

            data_list.append((bundleid, typedir, appgroupid, fileloc))

        self.data = data_list
