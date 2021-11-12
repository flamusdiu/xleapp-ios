from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class CallHistory(Artifact):
    def __post_init__(self) -> None:
        self.name = "Call History"
        self.category = "Call History"
        self.description = "Call History"
        self.web_icon = WebIcon.PHONE_CALL
        self.report_headers = (
            "Timestamp",
            "Phone Number",
            "Name",
            "Answered",
            "Call Type",
            "Call Direction",
            "Call Duration",
            "ISO Country Code",
            "Location",
            "Service Provider",
        )
        self.timeline = True

    @Search("**/CallHistory.storedata*")
    def process(self) -> None:
        for fp in self.found:
            if fp.path.suffix == ".storedata":
                cursor = fp().cursor()
                cursor.execute(
                    """
                    select
                    datetime(ZDATE+978307200,'unixepoch') as TIMESTAMP,
                    ZADDRESS,
                    ZNAME,
                    case ZANSWERED
                        when 0 then 'No'
                        when 1 then 'Yes'
                    end,
                    case ZCALLTYPE
                        when 0 then 'Third-Party App'
                        when 1 then 'Phone'
                        when 8 then 'FaceTime Video'
                        when 16 then 'FaceTime Audio'
                        else ZCALLTYPE
                    end,
                    case ZORIGINATED
                        when 0 then 'Incoming'
                        when 1 then 'Outgoing'
                    end,
                    strftime('%H:%M:%S',ZDURATION, 'unixepoch') as CALLDURATION,
                    upper(ZISO_COUNTRY_CODE),
                    ZLOCATION,
                    ZSERVICE_PROVIDER
                    from ZCALLRECORD
                    """,
                )

                all_rows = cursor.fetchall()
                if all_rows:
                    for row in all_rows:
                        an = str(row["ZADDRESS"])
                        an = an.replace("b'", "")
                        an = an.replace("'", "")
                        row_dict = dict_from_row(row)
                        self.data.append(
                            (row["TIMESTAMP"], an, *tuple(row_dict.values())[2:]),
                        )
