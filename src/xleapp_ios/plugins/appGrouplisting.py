import plistlib

from xleapp import Artifact, Search, WebIcon


class AppGroupListing(Artifact):
    def __post_init__(self) -> None:
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

    @Search(
        "*/private/var/mobile/Containers/Shared/AppGroup/*/*.metadata.plist",
        "**/PluginKitPlugin/*.metadata.plist",
    )
    def process(self):
        for fp in self.found:
            plist = plistlib.load(fp())
            bundleid = plist["MCMMetadataIdentifier"]

            path = fp.path
            appgroupid = path.parent.name
            fileloc = path.parent
            typedir = path.parents[1].name

            self.data.append((bundleid, typedir, appgroupid, fileloc))
