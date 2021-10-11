from dataclasses import dataclass

from xleapp import Artifact, Search, WebIcon, timed


@dataclass
class Accounts(Artifact):
    def __post_init__(self):
        self.name = "Accounts"
        self.category = "Accounts"
        self.web_icon = WebIcon.USER
        self.report_headers = (
            "Timestamp",
            "Account Desc.",
            "Username",
            "Description",
            "Identifier",
            "Bundle ID",
        )

    @timed
    @Search("**/Accounts3.sqlite")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                datetime(zdate+978307200,'unixepoch','utc' ),
                zaccounttypedescription,
                zusername,
                zaccountdescription,
                zaccount.zidentifier,
                zaccount.zowningbundleid
                from zaccount, zaccounttype
                where zaccounttype.z_pk=zaccount.zaccounttype
                """,
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
                self.data = data_list
