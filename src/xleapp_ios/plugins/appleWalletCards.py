import re

from xleapp import Artifact, Search, WebIcon


class AppleWalletCards(Artifact):
    def __post_init__(self) -> None:
        self.name = "Cards"
        self.category = "Apple Wallet"
        self.web_icon = WebIcon.CREDIT_CARD
        self.report_headers = (
            'Timestamp (Card Added)',
            'Card Number',
            'Expiration Date',
            'Type',
        )
        self.timeline = True

    @Search("*/com.apple.Passbook/Cache.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                SELECT
                TIME_STAMP,
                PROTO_PROPS
                FROM CFURL_CACHE_RESPONSE
                INNER JOIN CFURL_CACHE_BLOB_DATA ON CFURL_CACHE_BLOB_DATA.ENTRY_ID = CFURL_CACHE_RESPONSE.ENTRY_ID
                WHERE REQUEST_KEY LIKE '%CARDS'
                """,
            )

            all_rows = cursor.fetchall()

            if all_rows:

                def get_bank_card_number(card_information):
                    num_of_digits = [19, 18, 17, 16, 15, 14, 13]

                    for digit_num in num_of_digits:
                        found_entry = re.findall(
                            r'\d{{{digits}}}'.format(digits=digit_num),
                            card_information,
                        )
                        if found_entry:
                            return found_entry[0]

                def get_card_type(card_num, num_length):
                    first_digit = str(card_num)[:1]
                    first_two_digits = str(card_num)[:2]

                    if first_digit == '4' and (num_length == 13 or num_length == 16):
                        return 'Visa'
                    elif first_digit == '5' and num_length == 16:
                        return 'Mastercard'
                    elif first_digit == '6' and num_length == 16:
                        return 'Discover'
                    elif (
                        first_two_digits == '34' or first_two_digits == '37'
                    ) and num_length == 15:
                        return 'American Express'
                    elif (
                        first_two_digits == '30'
                        or first_two_digits == '36'
                        or first_two_digits == '38'
                    ) and num_length == 14:
                        return 'Diners Club Carte Blanche'
                    else:
                        return 'Unknown'

                for row in all_rows:
                    card_info = str(row["PROTO_PROPS"], 'utf-8', 'ignore')
                    card_number = get_bank_card_number(card_info)
                    expiration_date = re.findall(r'\d{2}/\d{2}', card_info)
                    card_type = get_card_type(card_number, len(card_number))

                    self.data.append(
                        (row["TIME_STAMP"], card_number, expiration_date[0], card_type),
                    )
