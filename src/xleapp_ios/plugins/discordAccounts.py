from xleapp import Artifact, Search, WebIcon
from xleapp.helpers.strings import filter_strings_in_file


class DiscordAccounts(Artifact):
    def __post_init__(self):
        self.name = "Discord Accounts"
        self.web_icon = WebIcon.MESSAGE_SQUARE
        self.category = "Discord"

    @Search(
        "*/var/mobile/Containers/Data/Application/*/Documents/mmkv/mmkv.default",
        file_names_only=True,
        return_on_first_hit=False,
    )
    def process(self) -> None:
        for fp in self.found:
            searchlist = [str(string) for string in filter_strings_in_file(fp())]

            cache = ""
            data_list = set()
            for counter, search_string in enumerate(searchlist, start=1):
                if "user_id_cache" in search_string:
                    cache = 'USER_ID_CACHE'
                if "email_cache" in search_string:
                    cache = "EMAIL_CACHE"
                if cache:
                    wf = searchlist[counter].split('"')
                    data_list.add((cache, wf[1]))
                    cache = ""

            self.data.extend(data_list)
