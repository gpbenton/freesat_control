# freesat_control
Python script to control freesat box

This script was inspired by https://github.com/Tyfy/POSHFreesat, which I have translated into python to run on my Raspberry Pi.

The ssdp discovery library came from https://gist.github.com/dankrause/6000248

# Usage

    import freesat

    freesat.sendRemoteCode(device_id, code)

examples:
    
    freesat.sendRemoteCode('FS-HMX-01A-0000-6A15', 415)
    
    freesat.sendRemoteKeys('FS-HMX-01A-0000-6A15', "Pause")
    freesat.sendRemoteKyes('FS-HMX-01A-0000-6A15', "106")
    
    p = freesat.getLocale('FS-HMX-01A-0000-6A15')
    print (p.response.locale.tuners.cdata)
    2

    p = freesat.getPowerStatus('FS-HMX-01A-0000-6A15')
    print (p.response.power['state'])
    on

    p = freesat.getNetflixStatus('FS-HMX-01A-0000-6A15')
    print (p.service.name.cdata)
    Netflix
    print (p.service.state.cdata)
    stopped


The device_id can be found in the settings/System Information/General Info page of your freesat box.  The device and key codes are at freeesat.keycodes
