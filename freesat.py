
import ssdp
import requests
import untangle
from urllib.error import URLError

deviceURL = {}
primaryRegion = {}
secondaryRegion = {}

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
    if "FS-HMX" not in serial_number:
        return "http://"+serial_number+":55016"
    if serial_number not in deviceURL:
        deviceURL[serial_number] = discoverFreesatBox(serial_number)

    return deviceURL[serial_number]

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
    else:
        for key in keys:
            sendRemoteKeys(serial_number, key)

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
    try:
        return untangle.parse(getDeviceURL(serial_number) + "/rc/locale")
    except URLError:
        del deviceURL[serial_number]
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
    try:
        return untangle.parse(getDeviceURL(serial_number) + "/rc/power")
    except (URLError):
        del deviceURL[serial_number]
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
    try:
        return untangle.parse(getDeviceURL(serial_number) + "/rc/apps/Netflix")
    except URLError:
        del deviceURL[serial_number]
        return untangle.parse(getDeviceURL(serial_number) + "/rc/apps/Netflix")

def getRegions(serial_number):
    """
    Return a tuple of primaryRegion, secondaryRegiion

    Raises requests.exceptions.HTTPError, as well as above exceptions
    """

    global primaryRegion, secondaryRegion

    if serial_number not in primaryRegion or\
            serial_number not in secondaryRegion:
        l = getLocale(serial_number)
        postcode = l.response.locale.postcode.cdata

        r = requests.get("http://fdp-sv09-channel-list-v2-0.gcprod1.freetime-platform.net/ms/channels/json/pcodelookup/g2/" + postcode)
        r.raise_for_status()
        j = r.json()
        primaryRegion[serial_number] = j["primaryRegion"]
        secondaryRegion[serial_number] = j["secondaryRegion"]

    return primaryRegion[serial_number], secondaryRegion[serial_number]

def getShowCaseEvents(serial_number):
    """
    Returns a python representation of json format of showcase events

    Raises ```requests.exceptions.HTTPError```, if the response was not success
    Raises ```ValueError``` if JSON was not decoded correctly
    """
    primaryRegion, secondaryRegion = getRegions(serial_number)

    r = requests.get("http://fdp-regional-v1-0.gcprod1.freetime-platform.net/ms3/regional/sc/json/{}/{}".format(primaryRegion, secondaryRegion))
    r.raise_for_status()
    return r.json()

def getOnDemandApps(serial_number):
    """
    Return a python representation of json format of OD players on device

    Raises ```requests.exceptions.HTTPError```, if the response was not success
    Raises ```ValueError``` if JSON was not decoded correctly
    """

    primaryRegion, secondaryRegion = getRegions(serial_number)

    r = requests.get("http://fdp-regional-v1-0.gcprod1.freetime-platform.net/ms3/regional/od/json/{}/{}".format(primaryRegion, secondaryRegion))
    r.raise_for_status()
    return r.json()

def getNowNextAll(serial_number):
    """
    Return a python representation of json format of Now and Next programs
    for each channel

    Raises ```requests.exceptions.HTTPError```, if the response was not success
    Raises ```ValueError``` if JSON was not decoded correctly
    """

    primaryRegion, secondaryRegion = getRegions(serial_number)

    r = requests.get("http://fdp-sv23-ms-ip-epg-v1-0.gcprod1.freetime-platform.net/json/nownextall/{}/{}".format(primaryRegion, secondaryRegion))
    r.raise_for_status()
    return r.json()

def getChannelList(serial_number):
    """
    Return a python representation of json format of the channel list

    Raises ```requests.exceptions.HTTPError```, if the response was not success
    Raises ```ValueError``` if JSON was not decoded correctly
    """

    primaryRegion, secondaryRegion = getRegions(serial_number)

    r = requests.get("http://fdp-sv09-channel-list-v2-0.gcprod1.freetime-platform.net/ms/channels/json/chlist/{}/{}".format(primaryRegion, secondaryRegion))
    r.raise_for_status()
    return r.json()

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
    "Info":457,
    "Record":416,
    "Exit":27,
    }
