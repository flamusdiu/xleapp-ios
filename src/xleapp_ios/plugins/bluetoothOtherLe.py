from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class BluetoothOtherLe(Artifact):
    def __post_init__(self) -> None:
        self.name = "Bluetooth Other LE"
        self.category = "Bluetooth"
        self.web_icon = WebIcon.BLUETOOTH
        self.report_headers = ("Name", "Address", "UUID")

    @Search("**/Library/Database/com.apple.MobileBluetooth.ledevices.other.db")
    def process(self):
        for fp in self.found:
            cursor = fp().cursor()

            cursor.execute(
                """
                    SELECT
                    Name,
                    Address,
                    Uuid
                    FROM
                    OtherDevices
                    order by Name desc
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
