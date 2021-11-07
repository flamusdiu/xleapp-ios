from xleapp import Artifact, Search, WebIcon


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

    @Search("**/passes23.sqlite")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                '''SELECT
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
                        '''
            )

            all_rows = cursor.fetchall()

        if len(all_rows) > 0:
            data_list = []
            for row in all_rows:
                data_list.append(
                    (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        row[6],
                        row[7],
                        row[8],
                        row[9],
                        row[10],
                        row[11],
                        row[12],
                        row[13],
                    )
                )
