from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FacebookMessengerContacts(Artifact):
    def __post_init__(self) -> None:
        self.name = "Contacts"
        self.category = "Facebook Messenger"
        self.report_headers = (
            "User ID",
            "Username",
            "Normalized Username",
            "Profile Pic URL",
            "Is App User",
        )
        self.web_icon = WebIcon.FACEBOOK

    @Search("**/lightspeed-*.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                id,
                name,
                normalized_name_for_search,
                profile_picture_url,
                case is_messenger_user
                    when 0 then ''
                    when 1 then 'Yes'
                end as is_messenger_user
                from contacts
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
