import io

import nska_deserialize as nd

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get


class CloudKitParticipants(Artifact):
    def __post_init__(self) -> None:
        self.name = "Participants"
        self.category = "CloudKit"
        self.web_icon = WebIcon.USER
        self.description = (
            "CloudKit Participants - CloudKit accounts participating "
            "in CloudKit shares."
        )
        self.report_headers = (
            "Record ID",
            "Email Address",
            "Phone Number",
            "Name Prefix",
            "First Name",
            "Middle Name",
            "Last Name",
            "Name Suffix",
            "Nickname",
        )

    @Search("*NoteStore.sqlite")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT Z_PK, ZSERVERSHAREDATA
                FROM
                ZICCLOUDSYNCINGOBJECT
                WHERE
                ZSERVERSHAREDATA NOT NULL
                """,
            )

            all_rows = cursor.fetchall()
            for row in all_rows:
                self.copyfile(
                    row["ZSERVERSHAREDATA"],
                    f"zserversharedata_{str(row['Z_PK'])}.bplist",
                    mode="wb",
                )

                pl = nd.deserialize_plist(io.BytesIO(row["ZSERVERSHAREDATA"]))
                for item in pl:
                    if "Participants" in item:
                        for pt in item.get("Participants"):
                            record_id = deep_get(
                                pt,
                                "UserIdentity",
                                "UserRecordID",
                                "RecordName",
                            )
                            email_address = deep_get(
                                pt,
                                "UserIdentity",
                                "LookupInfo",
                                "EmailAddress",
                            )
                            phone_number = deep_get(
                                pt,
                                "UserIdentity",
                                "LookupInfo",
                                "PhoneNumber",
                            )
                            first_name = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.givenName",
                            )
                            middle_name = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.middleName",
                            )
                            last_name = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.familyName",
                            )
                            name_prefix = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.namePrefix",
                            )
                            name_suffix = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.nameSuffix",
                            )
                            nickname = deep_get(
                                pt,
                                "UserIdentity",
                                "NameComponents",
                                "NS.nameComponentsPrivate",
                                "NS.nickname",
                            )

                            self.data.append(
                                (
                                    record_id,
                                    email_address,
                                    phone_number,
                                    name_prefix,
                                    first_name,
                                    middle_name,
                                    last_name,
                                    name_suffix,
                                    nickname,
                                ),
                            )
