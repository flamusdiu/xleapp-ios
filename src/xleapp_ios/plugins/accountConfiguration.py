import plistlib
from dataclasses import dataclass

from xleapp.artifacts.abstract import AbstractArtifact
from xleapp.helpers.decorators import Search, timed
from xleapp.report.webicons import Icon


@dataclass
class AccountConfiguration(AbstractArtifact):
    def __post_init__(self):
        self.name = 'Account Configuration'
        self.category = 'Accounts'
        self.web_icon = Icon.USER

    @timed
    @Search('**/com.apple.accounts.exists.plist')
    def process(self):
        data_list = []

        for fp in self.found:
            pl = plistlib.load(fp)
            for key, value in pl.items():
                data_list.append((key, value))

        self.data = data_list
