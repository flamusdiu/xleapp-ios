import plistlib

from xleapp import Artifact, Search, WebIcon


class AccountConfiguration(Artifact):
    def __post_init__(self):
        self.name = "Account Configuration"
        self.category = "Accounts"
        self.web_icon = WebIcon.USER

    @Search("**/com.apple.accounts.exists.plist")
    def process(self):
        data_list = []
        for fp in self.found:
            pl = plistlib.load(fp())
            for key, value in pl.items():
                data_list.append((key, value))

        self.data = data_list
