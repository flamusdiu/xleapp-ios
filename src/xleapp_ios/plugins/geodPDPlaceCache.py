import xleapp.helpers.strings as strings

from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class GeodPDPlaceCache(Artifact):
    def __post_init__(self) -> None:
        self.name = "GeoD PD Place Cache"
        self.category = "Locations"
        self.web_icon = WebIcon.MAP_PIN
        self.report_headers = (
            "last access time",
            "requestkey",
            "pdplacehash",
            "expire time",
            "pd place",
        )

    @Search("**/com.apple.geod/PDPlaceCache.db")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT
                datetime('2001-01-01', "lastaccesstime" || ' seconds') as lastaccesstime,
                requestkey,
                pdplacelookup.pdplacehash as pdplacehash,
                datetime('2001-01-01', "expiretime" || ' seconds') as expiretime,
                pdplace
                FROM pdplacelookup
                INNER JOIN pdplaces on pdplacelookup.pdplacehash = pdplaces.pdplacehash
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    pd_place = "".join(
                        f"{pd_row}<br>" for pd_row in set(strings.print(row["pdplace"]))
                    )
                    row_dict = dict_from_row(row)
                    self.data.append((*tuple(row_dict.values())[:4], pd_place))
