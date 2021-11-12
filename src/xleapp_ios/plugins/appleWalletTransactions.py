from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class AppleWalletTransactions(Artifact):
    def __post_init__(self) -> None:
        self.name = "Tranactions"
        self.category = "Apple Wallet"
        self.web_icon = WebIcon.DOLLAR_SIGN
        self.report_headers = (
            'Transaction Date',
            'Merchant',
            'Locality',
            'Administrative Area',
            'Currency Amount',
            'Currency Type',
            'Location Date',
            'Latitude',
            'Longitude',
            'Altitude',
            'Peer Payment Handle',
            'Payment Memo',
            'Transaction Status',
            'Transaction Type',
        )
        self.timeline = True

    @Search("**/passes23.sqlite")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                    SELECT
                    DATETIME(TRANSACTION_DATE + 978307200,'UNIXEPOCH'),
                    MERCHANT_NAME,
                    LOCALITY,
                    ADMINISTRATIVE_AREA,
                    CAST(AMOUNT AS REAL)/100,
                    CURRENCY_CODE,
                    DATETIME(LOCATION_DATE + 978307200,'UNIXEPOCH'),
                    LOCATION_LATITUDE,
                    LOCATION_LONGITUDE,
                    LOCATION_ALTITUDE,
                    PEER_PAYMENT_COUNTERPART_HANDLE,
                    PEER_PAYMENT_MEMO,
                    TRANSACTION_STATUS,
                    TRANSACTION_TYPE
                    FROM PAYMENT_TRANSACTION
                """,
            )

            all_rows = cursor.fetchall()

        if all_rows:
            for row in all_rows:
                row_dict = dict_from_row(row)
                self.data.append(tuple(row_dict.values()))
