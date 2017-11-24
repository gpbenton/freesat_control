
import ssdp
import requests
import untangle

deviceURL = ""

def discoverFreesatBox(serial_number):
    """
    Uses ssdp discovery to find Freesat stb with serial number (known as
    device id on front end).

    Raises ``RuntimeError`` if the device is not found
    """
    found_devices = ssdp.discover("urn:dial-multiscreen-org:service:dial:1")
    for device in found_devices:
        if device.location.endswith("xml"):
            obj = untangle.parse(device.location)
            if serial_number == obj.root.device.serialNumber.cdata:
                return device.location[:-11]

    raise RuntimeError("Device Not Found: {}".format(serial_number))

def getDeviceURL(serial_number):
    global deviceURL

    if deviceURL is "":
        deviceURL = discoverFreesatBox(serial_number)

    return deviceURL

def sendRemoteCode(serial_number, code):
    return requests.post(getDeviceURL(serial_number) + "/rc/remote",
      '<?xml version="1.0" ?><remote><key code="{}"/></remote>'.format(code))

def sendRemoteKeys(serial_number, keys):
    """
    Sends an iterable list of keypad keys.  If keys is recognized as a
    keyname, it sends that key, if not it attempts to send the iterable
    one by one.
    Raises ``RuntimeError`` if the device is not found or response was not 202
    example
        freesat.sendRemoteKeys('FS-HMX-01A-0000-6A15', "Play")
        freesat.sendRemoteKeys('FS-HMX-01A-0000-6A15', "702")
    """
    if keys in keycodes:
        r = sendRemoteCode(serial_number, keycodes[keys])
        if r.status_code is not 202:
            raise RuntimeError("Key {} received response: {}".format(keys, r))
        return

    for key in keys:
        r = sendRemoteCode(serial_number, keycodes[key])
        if r.status_code is not 202:
            raise RuntimeError("Key {} received response: {}".format(key, r))

"""
The following raise exceptions from untangle.parse()

    Raises ``ValueError`` if the first argument is None / empty string.
    Raises ``AttributeError`` if a requested xml.sax feature is not found in
    ``xml.sax.handler``.
    Raises ``xml.sax.SAXParseException`` if something goes wrong
    during parsing.
"""

def getLocale(serial_number):
    """
    Return python object representing locale
    from
    <?xml version="1.0" ?><response resource="/rc/locale"><locale><deviceid>FS-HMX-01A-0000-FFFF</deviceid><postcode>NN9</postcode><tuners>2</tuners></locale></response>
    example:
        import freesat

        p = freesat.getLocale('FS-HMX-01A-0000-6A15')
        print (p.response.locale.tuners.cdata)
        2

    """
    return untangle.parse(getDeviceURL(serial_number) + "/rc/locale")

def getPowerStatus(serial_number):
    """
    Return python object representing power status
    from 
    <?xml version="1.0" ?><response resource="/rc/power"><power state="on" transitioning-to="" no-passive-standby="true" /></response>
    example:
        import freesat
        p = freesat.getPowerStatus('FS-HMX-01A-0000-6A15')
        print (p.response.power['state'])
        on
    """
    return untangle.parse(getDeviceURL(serial_number) + "/rc/power")

def getNetflixStatus(serial_number):
    """
    Return python object representing netflix status
    from
    <?xml version="1.0" encoding="UTF-8"?>
    <service xmlns="urn:dial-multiscreen-org:schemas:dial" dialVer="1.7">
      <name>Netflix</name>
      <options allowStop="true"/>
      <state>stopped</state>
    </service>
    exmaple:
        p = freesat.getNetflixStatus('FS-HMX-01A-0000-6A15')
        print (p.service.name.cdata)
        Netflix
        print (p.service.state.cdata)
        stopped
    """
    return untangle.parse(getDeviceURL(serial_number) + "/rc/apps/Netflix")

keycodes = {
    "OK":13,
    "Pause":19,
    "Exit":27,
    "Left":37,
    "Up":38,
    "Right":39,
    "Down":40,
    "0":48,
    "1":49,
    "2":50,
    "3":51,
    "4":52,
    "5":53,
    "6":54,
    "7":55,
    "8":56,
    "9":57,
    "Red":403,
    "Green":404,
    "Yellow":405,
    "Blue":406,
    "Rewind":412,
    "Play":415,
    "Fast Forward":417,
    "Previous":424,
    "Next":425,
    "Channel Up":427,
    "Channel Down":428,
    "Volume Up":447,
    "Volume Down":448,
    "Mute":449,
    "Audio Description":450,
    "Subtitles":460,
    "Back":461,
    }
