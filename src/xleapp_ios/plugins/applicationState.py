import io
import plistlib

import nska_deserialize as nd

from xleapp import Artifact, Search, WebIcon


class ApplicationState(Artifact):
    def __post_init__(self):
        self.name = "Application State"
        self.category = "Installed Apps"
        self.web_icon = WebIcon.PACKAGE
        self.report_headers = ("Bundle ID", "Bundle Path", "Sandbox Path")

    @Search("**/applicationState.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select ait.application_identifier as ai, kvs.value as compat_info,
                (SELECT kvs.value from kvs left join application_identifier_tab on application_identifier_tab.id = kvs.application_identifier
                left join key_tab on kvs.key = key_tab.id
                WHERE key_tab.key="XBApplicationSnapshotManifest" and kvs.key = key_tab.id
                and application_identifier_tab.id = ait.id
                ) as snap_info
                from kvs
                left join application_identifier_tab ait on ait.id = kvs.application_identifier
                left join key_tab on kvs.key = key_tab.id
                where key_tab.key="compatibilityInfo"
                order by ait.id
                """,
            )

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            data_list = []
            snap_info_list = []
            for row in all_rows:
                plist_file_object = io.BytesIO(row[1])
                if row[1].find(b"NSKeyedArchiver") == -1:
                    plist = plistlib.load(plist_file_object)
                else:
                    try:
                        plist = nd.deserialize_plist(plist_file_object)
                    except (
                        nd.DeserializeError,
                        nd.biplist.NotBinaryPlistException,
                        nd.biplist.InvalidPlistException,
                        nd.plistlib.InvalidFileException,
                        nd.ccl_bplist.BplistError,
                        ValueError,
                        TypeError,
                        OSError,
                        OverflowError,
                    ) as ex:
                        self.log(
                            message=(
                                f"Failed to read plist for {row[0]}, "
                                f"error was: {ex!r}"
                            ),
                        )
                if plist:
                    if type(plist) is dict:
                        var1 = plist.get("bundleIdentifier", "")
                        var2 = plist.get("bundlePath", "")
                        var3 = plist.get("sandboxPath", "")
                        data_list.append((var1, var2, var3))
                        if row[2]:
                            snap_info_list.append((var1, var2, var3, row[2]))
                    else:
                        self.log(
                            message=(
                                f"For {row[0]} Unexpected type {type(plist)!r} "
                                "found as plist root, can't process"
                            ),
                        )
                else:
                    self.log(message=f"For {row[0]!r}, plist could not be read!")
