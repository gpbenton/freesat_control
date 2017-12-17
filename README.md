# freesat_control
Python script to control freesat box

This script was inspired by https://github.com/Tyfy/POSHFreesat, which I have translated into python to run on my Raspberry Pi.

The ssdp discovery library came from https://gist.github.com/dankrause/6000248

# Usage

    from freesat import Freesat
    p = Freesat("FS-HMX-01A-0000-6A15")

or 

    p = Freesat("192.168.0.3")

examples:
    
    p.sendRemoteCode(415)
    
    p.sendRemoteKeys("Pause")
    p.sendRemoteKeys("106")
    p.sendRemoteKeys(("Play", "106"))
    
    l = p.getLocale()
    print (l.response.locale.tuners.cdata)
    2

    s = p.getPowerStatus()
    print (s.response.power['state'])
    on

    t = p.getNetflixStatus()
    print (t.service.name.cdata)
    Netflix
    print (t.service.state.cdata)
    stopped


The device_id can be found in the settings/System Information/General Info page of your freesat box.  The device and key codes are at freeesat.keycodes
