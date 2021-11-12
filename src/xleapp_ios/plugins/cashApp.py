from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class CashApp(Artifact):
    def __post_init__(self) -> None:
        self.name = "Transactions"
        self.category = "Cash App"
        self.web_icon = WebIcon.CREDIT_CARD
        self.report_headers = (
            "Transaction Date",
            "Display Name",
            "Cashtag",
            "Account Owner Role",
            "Currency Amount",
            "Transaction State",
            "Transaction State",
        )
        self.timeline = True

    @Search(
        (
            "**private/var/mobile/Containers/Shared/AppGroup/*/"
            "CCEntitySync-api.squareup.com.sqlite"
        ),
    )
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """SELECT
--Unix Epoch timestamp for the transaction display time.
datetime(ZPAYMENT.ZDISPLAYDATE/1000.0,'unixepoch') as "TRANSACTION DISPLAY DATE",

--Full name of the customer as entered into the "First Name" and "Last Name" fields upon application setup.
LTRIM(SUBSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), INSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB)),
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST('","is_cash' AS BLOB)) -
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"full_name":' AS BLOB))), ',"full_name":"') AS 'CUSTOMER FULL DISPLAY NAME',

--Customer's username created upon application setup.
CASE WHEN INSTR(ZSYNCCUSTOMER, '"cashtag":null') THEN '***NO CASH TAG***' WHEN ZSYNCCUSTOMER LIKE '%C_INCOMING_TRANSFER%' THEN '***NO CASH TAG***' ELSE
LTRIM(SUBSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), INSTR(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"cashtag":' AS BLOB)),
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST('","is_verification' AS BLOB)) -
instr(CAST(ZCUSTOMER.ZSYNCCUSTOMER AS BLOB), CAST(',"cashtag":' AS BLOB))), ',"cashtag":"') END CASHTAG,

-- Description of the role of the user account signed into the CashApp application of the device.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"RECIPIENT"%' THEN 'RECIPIENT' ELSE 'SENDER' END AS "Account Owner Role",

--Transaction amount sent/received between the account user and customer
printf("$%.2f", LTRIM( SUBSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), INSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('{"amount":' AS BLOB)),
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"currency' AS BLOB)) -
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('ount":' AS BLOB)) - 6), '{"amount":') / 100.0) AS 'Transaction Amount',

--State of the transaction. Certain times the user may have to accept or decline a payment or payment request from the sender.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"COMPLETED"%' THEN 'COMPLETED' WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"CANCELED"%' THEN 'CANCELED' ELSE 'WAITING ON RECIPIENT' END AS 'Transaction State',

--Note provided by the sender. Like a memo line on a bank check.
CASE WHEN ZPAYMENT.ZSYNCPAYMENT LIKE '%"note"%' THEN LTRIM( SUBSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), INSTR(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"note":' AS BLOB)),
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST(',"sent' AS BLOB)) -
instr(CAST(ZPAYMENT.ZSYNCPAYMENT AS BLOB), CAST('"note":' AS BLOB))), ',"note":') ELSE '***NO NOTE PRESENT***' END NOTE,

FROM ZPAYMENT
INNER JOIN ZCUSTOMER ON ZCUSTOMER.Z
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
