# freesat_control
Python script to control freesat box

This script was inspired by https://github.com/Tyfy/POSHFreesat, which I have translated into python to run on my Raspberry Pi.

The ssdp discovery library came from https://gist.github.com/dankrause/6000248

# Usage

    import freesat_control

    freesat_control.sendRemoteCode(device_id, code)

example:
    
    freesat_control.sendRemoteCode('FS-HMX-01A-0000-6A15', 415)

The device_id can be found in the settings/System Information/General Info page of your freesat box.  The device codes are at https://github.com/Tyfy/POSHFreesat/blob/master/freesat.ps1
