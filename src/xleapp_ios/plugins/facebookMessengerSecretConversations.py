from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FacebookMessengerSecretConversations(Artifact):
    def __post_init__(self) -> None:
        self.name = "Secret Conversations"
        self.category = "Facebook Messenger"
        self.report_headers = (
            "Timestamp",
            "Thread Key",
            "Sender Name",
            "Message (Encrypted)",
            "Attachment (Encrypted)",
        )

        self.web_icon = WebIcon.FACEBOOK

    @Search("**/lightspeed-*.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                 select
                datetime(secure_messages.timestamp_ms/1000,'unixepoch') as 'Timestamp',
                secure_messages.thread_key,
                contacts.name as 'Sender',
                secure_messages.text,
                secure_messages.secure_message_attachments_encrypted
                from secure_messages
                left join contacts
                    on secure_messages.sender_id = contacts.id
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
