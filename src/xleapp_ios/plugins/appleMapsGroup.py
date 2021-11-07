import plistlib

import blackboxprotobuf

from xleapp import Artifact, Search, WebIcon


class AppleMapsGroup(Artifact):
    def __post_init__(self) -> None:
        self.name = "Apple Maps Group"
        self.category = "Locations"
        self.web_icon = WebIcon.MAP_PIN
        self.report_headers = ('Latitude', 'Longitude')

    @Search("**/Shared/AppGroup/*/Library/Preferences/group.com.apple.Maps.plist")
    def process(self) -> None:
        for fp in self.found:
            deserialized_plist = plistlib.load(fp())
            types = {
                '1': {
                    'type': 'message',
                    'message_typedef': {
                        '1': {'type': 'int', 'name': ''},
                        '2': {'type': 'int', 'name': ''},
                        '5': {
                            'type': 'message',
                            'message_typedef': {
                                '1': {'type': 'double', 'name': 'Latitude'},
                                '2': {'type': 'double', 'name': 'Longitude'},
                                '3': {'type': 'double', 'name': ''},
                                '4': {'type': 'fixed64', 'name': ''},
                                '5': {'type': 'double', 'name': ''},
                            },
                            'name': '',
                        },
                        '7': {'type': 'int', 'name': ''},
                    },
                    'name': '',
                }
            }
            internal_deserialized_plist, di = blackboxprotobuf.decode_message(
                (deserialized_plist['MapsActivity']), types
            )

            latitude = internal_deserialized_plist['1']['5']['Latitude']
            longitude = internal_deserialized_plist['1']['5']['Longitude']

            data_list = []
            data_list.append((latitude, longitude))
        self.data = data_list
