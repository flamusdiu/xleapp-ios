from xleapp import Artifact, Search, WebIcon


class ConnectedDevices(Artifact):
    def __post_init__(self) -> None:
        self.name = "Connected Devices"
        self.category = "Connected to"
        self.web_icon = WebIcon.ZAP
        self.report_headers = ("User & Computer Names",)

    @Search("**/iTunes_Control/iTunes/iTunesPrefs")
    def process(self) -> None:
        for fp in self.found:
            data = fp().read()
            userComps = ""

            self.log(
                message=(
                    "-> Data being interpreted for FRPD is of type: " f"{str(type(data))}"
                ),
            )

            byteArr = bytearray(data)
            userByteArr = bytearray()

            magicOffset = byteArr.find(b"\x01\x01\x80\x00\x00")
            magic = byteArr[magicOffset : magicOffset + 5]

            flag = 0

            if magic == b"\x01\x01\x80\x00\x00":
                self.log(
                    message=(
                        "-> Found magic bytes in iTunes Prefs FRPD... Finding Usernames "
                        "and Desktop names now"
                    ),
                )
                for offset in range(int(magicOffset + 92), len(data)):
                    if (data[offset]) == 0:
                        offset = int(magicOffset) + 157
                        if userByteArr.decode() == "":
                            continue
                        else:
                            if flag == 0:
                                userComps += f"{userByteArr.decode()} - "
                                flag = 1
                            else:
                                userComps += f"{userByteArr.decode()}\n"
                                flag = 0
                            userByteArr = bytearray()
                            continue
                    else:
                        char = data[offset]
                        userByteArr.append(char)
            self.data.append((userComps,))
