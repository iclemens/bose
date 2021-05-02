Bose Protocol
-------------

This repository tracks my efforts to reverse engineer the Bose NC 700 firmware upgrade process. The goal is to make it easy to downgrade the device to an older version.

The *wireshark* directory contains a protocol dissector which makes it easier to view the USB firmware upgrade.

The *python* directory contains some test code that attempts to interface with the NC 700 over either Bluetooth or USB. The protocol is identical, except that messages sent over USB have [0x0c, LL, LL] prepended where LL is the (big endian) packet length. Messaged received have [0x0d] prepended.

Firmware update
---------------

Data is sent using function 0x03 0x08 and operation 0x05 (start). 

[0x03, 0x08, 0x05, 0xff, 0x00, data...]

with 0xff being the length of the payload (including the offset) and 0x00 seems to be some kind of package number.

Hardware
--------

 - Qualcomm CSRA68105

Firmware format
---------------

Contains multiple parts, each part starts with an 8 byte identifier, followed by a 4 byte length. The parts I've seen so far:
 - APPUHDR# with # the version number
 - PARTDATA with 2 byte part type and 2 byte part number followed by data
 - APPUPFTR footer

Useful resources:

- https://developer.qualcomm.com/qfile/34081/csr102x_otau_overview.pdf
- https://github.com/bosefirmware/BoseConnect-Linux_based-connect
