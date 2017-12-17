
import ssdp
import requests
import untangle
from urllib.error import URLError
import nmap

class Freesat():

    class Freesat_sn:
        def __init__(self, serial_number):
            self.serial_number = serial_number
            self.deviceURL = self._discoverFreesatBox()

        def _discoverFreesatBox(self):
            """
            Uses ssdp discovery to find Freesat stb with serial number (known as
            device id on front end).

            Raises ``RuntimeError`` if the device is not found
            """
            found_devices = ssdp.discover("urn:dial-multiscreen-org:service:dial:1")
            for device in found_devices:
                if device.location.endswith("xml"):
                    obj = untangle.parse(device.location)
                    if self.serial_number == obj.root.device.serialNumber.cdata:
                        return device.location[:-11]

            raise RuntimeError("Device Not Found: {}".format(self.serial_number))

        def _resetURL(self):
            del self.deviceURL
            self.getDeviceURL()

        def getDeviceURL(self):
            if not hasattr(self, "deviceURL"):
                self.deviceURL = self._discoverFreesatBox()
            return self.deviceURL


    class Freesat_ip:
        """
        Takes an ip address and uses nmap to determine the port.
        nmap raises a KeyError when the IP address is incorrect.
        When the port changes, a requests.exceptions.ConnectionError is raised
        """
        def __init__(self, ip):
            try:
                self.ip = ip
                self.getDeviceURL()
            except (KeyError):
                raise RuntimeError("Device Not Found: {}".format(ip))

        def _get_port(self):
            """
              Gets the port in use.

              Raises KeyError if device not found
            """
            nm = nmap.PortScanner()
            # Assume port is above 60000 to save time scanning.
            # may need adjusting
            nm.scan(self.ip, arguments='-p T:60000-65535')
            return nm[self.ip].all_tcp()[0]

        def _resetURL(self):
            try:
                del self.url
                self.getDeviceURL()
            except (KeyError):
                raise RuntimeError("Device Not Found: {}".format(ip))


        def getDeviceURL(self):
            if not hasattr(self, "url"):
                self.port = self._get_port()
                self.url = "http://" + self.ip + ":" + str(self.port)
            return self.url


    def __init__(self, id):
        if self.isSerialNumber(id):
            self.freesat = self.Freesat_sn(id)
        else:
            self.freesat = self.Freesat_ip(id)

    def isSerialNumber(self, id):
        return id.startswith("FS-HMX")

    def sendRemoteCode(self, code):
        try:
            return requests.post(self.freesat.getDeviceURL() + "/rc/remote",
              '<?xml version="1.0" ?><remote><key code="{}"/></remote>'.format(code))
        except (requests.exceptions.ConnectionError, URLError):
            self.freesat._resetURL()
            return requests.post(self.freesat.getDeviceURL() + "/rc/remote",
              '<?xml version="1.0" ?><remote><key code="{}"/></remote>'.format(code))


    def sendRemoteKeys(self, keys):
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
            r = self.sendRemoteCode(keycodes[keys])
            if r.status_code is not 202:
                raise RuntimeError("Key {} received response: {}".format(keys, r))
        else:
            for key in keys:
                self.sendRemoteKeys(key)

    """
    The following raise exceptions from untangle.parse()

        Raises ``ValueError`` if the first argument is None / empty string.
        Raises ``AttributeError`` if a requested xml.sax feature is not found in
        ``xml.sax.handler``.
        Raises ``xml.sax.SAXParseException`` if something goes wrong
        during parsing.
    """

    def getLocale(self):
        """
        Return python object representing locale
        from
        <?xml version="1.0" ?><response resource="/rc/locale"><locale><deviceid>FS-HMX-01A-0000-FFFF</deviceid><postcode>NN9</postcode><tuners>2</tuners></locale></response>
        example:
            import freesat

            r = freesat.Freesat('FS-HMX-01A-0000-6A15')
            p = r.getLocale()
            print (p.response.locale.tuners.cdata)
            2

        """
        try:
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/locale")
        except (requests.exceptions.ConnectionError, URLError):
            self.freesat._resetURL()
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/locale")

    def getPowerStatus(self):
        """
        Return python object representing power status
        from 
        <?xml version="1.0" ?><response resource="/rc/power"><power state="on" transitioning-to="" no-passive-standby="true" /></response>
        example:
            import freesat
            r = freesat.Freesat('FS-HMX-01A-0000-6A15')
            p = r.getPowerStatus()
            print (p.response.power['state'])
            on
        """
        try:
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/power")
        except (requests.exceptions.ConnectionError, URLError):
            self.freesat._resetURL()
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/power")

    def getNetflixStatus(self):
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
            p = r.getNetflixStatus()
            print (p.service.name.cdata)
            Netflix
            print (p.service.state.cdata)
            stopped
        """
        try:
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/apps/Netflix")
        except (requests.exceptions.ConnectionError, URLError):
            self.freesat._resetURL()
            return untangle.parse(self.freesat.getDeviceURL() + "/rc/apps/Netflix")

    def getRegions(self):
        """
        Return a tuple of primaryRegion, secondaryRegiion

        Raises requests.exceptions.HTTPError, as well as above exceptions
        """

        if (not hasattr(self, "primaryRegion")) or  (not hasattr(self, "secondaryRegion")):
            l = self.getLocale()
            postcode = l.response.locale.postcode.cdata

            r = requests.get("http://fdp-sv09-channel-list-v2-0.gcprod1.freetime-platform.net/ms/channels/json/pcodelookup/g2/" + postcode)
            r.raise_for_status()
            j = r.json()
            self.primaryRegion = j["primaryRegion"]
            self.secondaryRegion = j["secondaryRegion"]

        return self.primaryRegion, self.secondaryRegion

    def getShowCaseEvents(self):
        """
        Returns a python representation of json format of showcase events

        Raises ```requests.exceptions.HTTPError```, if the response was not success
        Raises ```ValueError``` if JSON was not decoded correctly
        """
        primaryRegion, secondaryRegion = self.getRegions()

        r = requests.get("http://fdp-regional-v1-0.gcprod1.freetime-platform.net/ms3/regional/sc/json/{}/{}".format(primaryRegion, secondaryRegion))
        r.raise_for_status()
        return r.json()

    def getOnDemandApps(self):
        """
        Return a python representation of json format of OD players on device

        Raises ```requests.exceptions.HTTPError```, if the response was not success
        Raises ```ValueError``` if JSON was not decoded correctly
        """

        primaryRegion, secondaryRegion = self.getRegions()

        r = requests.get("http://fdp-regional-v1-0.gcprod1.freetime-platform.net/ms3/regional/od/json/{}/{}".format(primaryRegion, secondaryRegion))
        r.raise_for_status()
        return r.json()

    def getNowNextAll(self):
        """
        Return a python representation of json format of Now and Next programs
        for each channel

        Raises ```requests.exceptions.HTTPError```, if the response was not success
        Raises ```ValueError``` if JSON was not decoded correctly
        """

        primaryRegion, secondaryRegion = self.getRegions()

        r = requests.get("http://fdp-sv23-ms-ip-epg-v1-0.gcprod1.freetime-platform.net/json/nownextall/{}/{}".format(primaryRegion, secondaryRegion))
        r.raise_for_status()
        return r.json()

    def getChannelList(self):
        """
        Return a python representation of json format of the channel list

        Raises ```requests.exceptions.HTTPError```, if the response was not success
        Raises ```ValueError``` if JSON was not decoded correctly
        """

        primaryRegion, secondaryRegion = self.getRegions()

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
