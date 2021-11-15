import io

import nska_deserialize as nd

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.utils import deep_get


class CloudKitSharing(Artifact):
    def __post_init__(self):
        self.name = "CloudKit Note Sharing"
        self.category = "CloudKit"
        self.web_icon = WebIcon.SHARE_2
        self.report_headers = (
            "Record ID",
            "Record Type",
            "Creation Date",
            "Creator ID",
            "Modified Date",
            "Modifier ID",
            "Modifier Device",
        )
        self.description = (
            "CloudKit Note Sharing - Notes information shared via CloudKit."
            "Look up the Record ID in the ZICCLOUDSYYNCINGOBJECT.ZIDENTIFIER column. "
        )

    @Search("*NoteStore.sqlite")
    def process(self) -> None:
        for fp in self.found:

            cursor = fp().cursor()
            cursor.execute(
                """
                    select z_pk, zserverrecorddata
                    from
                    ziccloudsyncingobject
                    where
                    zserverrecorddata not null
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    self.copyfile(
                        row["zserverrecorddata"],
                        f"zserversharedata_{str(row['z_pk'])}.bplist",
                    )

                    pl = nd.deserialize_plist(io.BytesIO(row["zserverrecorddata"]))

                    pl_dict = {}
                    for item in pl:
                        pl_dict.update(item)

                    creation_date = deep_get(pl_dict, "RecordCtime")
                    last_modified_date = deep_get(pl_dict, "RecordMtime")
                    last_modified_id = deep_get(
                        pl_dict,
                        "LastModifiedUserRecordID",
                        "RecordName",
                    )
                    creator_id = deep_get(pl_dict, "CreatorUserRecordID", "RecordName")
                    last_modified_device = deep_get(pl_dict, "ModifiedByDevice")
                    record_type = deep_get(pl_dict, "RecordType")
                    record_id = deep_get(pl_dict, "RecordID", "RecordName")

                    self.data.append(
                        (
                            record_id,
                            record_type,
                            creation_date,
                            creator_id,
                            last_modified_date,
                            last_modified_id,
                            last_modified_device,
                        ),
                    )
