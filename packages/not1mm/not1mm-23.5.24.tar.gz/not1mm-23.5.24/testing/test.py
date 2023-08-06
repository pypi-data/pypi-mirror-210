"""doc"""

import socket
from xml.dom.minidom import parseString
from dicttoxml import dicttoxml

contact_info = {
    "app": "NOT1MM",
    "contestname": "CQWPXCW",
    "contestnr": "1",
    "timestamp": "",
    "mycall": "K6GTE",
    "operator": "K6GTE",
    "band": "14",
    "rxfreq": "1402500",
    "txfreq": "1402500",
    "mode": "CW",
    "call": "W1AW",
    "countryprefix": "K",
    "wpxprefix": "W1",
    "stationprefix": "K6GTE",
    "continent": "NA",
    "snt": "59",
    "sntnr": "2",
    "rcv": "59",
    "rcvnr": "34",
    "gridsquare": "",
    "exchange1": "",
    "section": "",
    "comment": "",
    "qth": "",
    "name": "",
    "power": "",
    "misctext": "",
    "zone": "5",
    "prec": "",
    "ck": "0",
    "ismultiplier1": "1",
    "ismultiplier2": "0",
    "ismultiplier3": "0",
    "points": "1",
    "radionr": "1",
    "RoverLocation": "",
    "RadioInterfaced": "0",
    "NetworkedCompNr": "0",
    "IsOriginal": True,
    "NetBiosName": "DESKTOP-EGCUFGO",
    "IsRunQSO": 0,
    "Run1Run2": "1",
    "ContactType": "",
    "StationName": "DESKTOP-EGCUFGO",
    "ID": "36ad91ae258d48119534c442e7876156",
    "IsClaimedQso": 1,
    "oldcall": "W1AW",
}

package_name = "contactinfo"

bytes_to_send = dicttoxml(
    contact_info,
    custom_root=package_name,
    attr_type=False,
    return_bytes=False,
    encoding="UTF-8",
)
dom = parseString(bytes_to_send)
output = dom.toprettyxml(indent="\t", newl="\r\n").encode()
print(f"{output}")

network_list = "127.0.0.1:12061 0.0.0.0:12061"
for network in network_list.split():
    print(network)
    addr, port = network.split(":")
    print(f"Address: {addr}, Port: {port}")
    radio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    try:
        radio_socket.sendto(
            output,
            (addr, int(port)),
        )
    except PermissionError as the_error:
        print(f"{the_error}")
