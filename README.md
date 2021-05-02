Bose Protocol
-------------

This repository tracks my efforts to reverse engineer the Bose NC 700 firmware upgrade process. The goal is to make it easy to downgrade the device to an older version.

The *wireshark* directory contains a protocol dissector which makes it easier to view the USB firmware upgrade.

The *python* directory contains some test code that attempts to interface with the NC 700 over either Bluetooth or USB. The protocol is identical, except that messages sent over USB have [0x0c, LL, LL] prepended where LL is the (big endian) packet length. Messaged received have [0x0d] prepended.
