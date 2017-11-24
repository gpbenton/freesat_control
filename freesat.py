
import ssdp
import requests
import untangle

deviceURL = ""

def discoverFreesatBox(serial_number):
    """
    Uses ssdp discovery to find Freesat stb with serial number (known as
    device id on front end).

    Raises ``NameError`` if the device is not found
    """
    found_devices = ssdp.discover("urn:dial-multiscreen-org:service:dial:1")
    for device in found_devices:
        if device.location.endswith("xml"):
            obj = untangle.parse(device.location)
            if serial_number == obj.root.device.serialNumber.cdata:
                return device.location[:-11]

    raise NameError("Device Not Found: {}".format(serial_number))

def getDeviceURL(serial_number):
    global deviceURL

    if deviceURL is "":
        deviceURL = discoverFreesatBox(serial_number)

    return deviceURL

def sendRemoteCode(serial_number, code):
    return requests.post(getDeviceURL(serial_number) + "/rc/remote",
      '<?xml version="1.0" ?><remote><key code="{}"/></remote>'.format(code))

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
