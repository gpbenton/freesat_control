
import ssdp
import requests
import untangle

deviceURL = ""

def discoverFreesatBox(serial_number):
    found_devices = ssdp.discover("urn:dial-multiscreen-org:service:dial:1")
    for device in found_devices:
        if device.location.endswith("xml"):
            obj = untangle.parse(device.location)
            if serial_number == obj.root.device.serialNumber.cdata:
                return device.location[:-11]

    raise NameError("Device Not Found: {}".format(serial_number))

def sendRemoteCode(serial_number, code):
    global deviceURL

    if deviceURL is "":
        deviceURL = discoverFreesatBox(serial_number)

    return requests.post(deviceURL + "/rc/remote",
      '<?xml version="1.0" ?><remote><key code="{}"/></remote>'.format(code))



