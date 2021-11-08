import xleapp.helpers.strings as strings

from xleapp import Artifact, Search, WebIcon


class GeodPDPlaceCache(Artifact):
    def __post_init__(self):
        self.name = "PD Place Cache"
        self.category = "Geolocation"
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
                SELECT requestkey, pdplacelookup.pdplacehash, datetime('2001-01-01', "lastaccesstime" || ' seconds') as lastaccesstime, datetime('2001-01-01', "expiretime" || ' seconds') as expiretime, pdplace
                FROM pdplacelookup
                INNER JOIN pdplaces on pdplacelookup.pdplacehash = pdplaces.pdplacehash
                """,
            )

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)

            if usageentries > 0:
                data_list = []
                for row in all_rows:
                    pd_place = "".join(f"{row}<br>" for row in set(strings.print(row[4])))
                    data_list.append((row[2], row[0], row[1], row[3], pd_place))
                self.data = data_list
