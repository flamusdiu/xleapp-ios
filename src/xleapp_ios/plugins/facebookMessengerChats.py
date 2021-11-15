from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.db import dict_from_row


class FacebookMessengerChats(Artifact):
    def __post_init__(self) -> None:
        self.name = "Chats"
        self.category = "Facebook Messenger"
        self.web_icon = WebIcon.FACEBOOK
        self.report_headers = (
            "Timestamp",
            "Sender Name",
            "Sender ID",
            "Message",
            "Attachment",
            "Attachment Name",
            "Attachment Size",
            "Title Text",
        )

    @Search("**/lightspeed-*.db")
    def process(self) -> None:
        for fp in self.found:
            cursor = fp().cursor()
            cursor.execute(
                """
                select
                datetime(thread_messages.timestamp_ms/1000,'unixepoch') as Timestamp,
                contacts.name as 'Sender Name',
                thread_messages.thread_key,
                thread_messages.text as 'Message',
                case thread_messages.has_attachment
                    when NULL then ''
                    when 1 then 'Yes'
                end as Attachment,
                attachments.filename as 'Attachment Name',
                attachments.filesize as 'Attachment Size',
                attachment_items.title_text
                from thread_messages
                left join contacts
                    on thread_messages.sender_id = contacts.id
                left join attachments
                    on thread_messages.message_id = attachments.message_id
                left join attachment_items
                    on thread_messages.message_id = attachment_items.message_id
                where attachment_items.title_text IS NULL or attachment_items.title_text like 'Location sharing ended'
                order by Timestamp
                """,
            )

            all_rows = cursor.fetchall()
            if all_rows:
                for row in all_rows:
                    row_dict = dict_from_row(row)
                    self.data.append(tuple(row_dict.values()))
