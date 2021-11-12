import plistlib

from xleapp import Artifact, Search, WebIcon


class AccountConfiguration(Artifact):
    def __post_init__(self) -> None:
        self.name = "Account Configuration"
        self.category = "Accounts"
        self.web_icon = WebIcon.USER

    @Search("**/com.apple.accounts.exists.plist")
    def process(self):
        for fp in self.found:
            pl = plistlib.load(fp())
            for item in pl.items():
                self.data.append(item)
