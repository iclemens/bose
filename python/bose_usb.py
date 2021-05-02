import sys
import usb.core
import usb.util
import struct

dev = usb.core.find(idVendor=0x05a7, idProduct=0x40fc)

if dev.is_kernel_driver_active(0):
    try:
        dev.detach_kernel_driver(0)
        print("kernel driver detached")
    except usb.core.USBError as e:
        sys.exit("Could not detach kernel driver: %s" % str(e))

dev.set_configuration()
dev.reset()

bmRequest = usb.util.build_request_type(
    direction=usb.util.CTRL_OUT,
    type = usb.util.CTRL_TYPE_STANDARD,
    recipient=usb.util.CTRL_RECIPIENT_INTERFACE
)

def bose_error(code):
    if code in BOSE_ERRORS:
        return RuntimeError(BOSE_ERRORS[code])
    return RuntimeError('Unknown error')

def bose_get(block, func):
    request = bytes([0x0c, 0x00, 0x04, block, func, 0x01, 0x00])
    dev.write(0x02, request, 1000)
    res = dev.read(0x081, 1024, 1000)

    if res[0] != 0x0d:
        raise RuntimeError('Invalid report id.')
    if res[1] != block or res[2] != func:
        raise RuntimeError('Function block and/or id do not match.')

    if res[3] == 0x04:
        raise bose_error(res[5])

    if res[3] != 0x03:
        raise RuntimeError(f'Operator not supported: {res[3]:02x}.')

    len = res[4]
    return res[5:5+len]

def parse_bass(data):
    records = {}
    labels = ['bass', 'mid', 'treble']
    for i in range(len(data) // 4):
        (min, max, value, type) = struct.unpack('bbbb', bytes(data[i*4:4+i*4]))
        records[labels[type]] = { 'min': min, 'max': max, 'value': value }
    return records




#  array('B', [100, 4, 57, 0]) => 18 hours 1min / 100%
# [11, 2, 0] => nc off
# [11, 5, 0]) 10, 5, 0 + on + remember
# [11, 8, 0]) 8, 4, 2 + on + remember
# [11, 8, 1]) 8, 4, 2 + on / no remember
# [11, 10, 1]) => 0, 0, 0 + on / remember


# CNC => 11, 0, 1 => NC level 10
# CNC => 11, 1, 1 => NC level 9
# CNC => 11, 2, 1 => NC level 8
# CNC => 11, 3, 1 => NC level 7
# CNC => 11, 10, 1 => NC level 7

def get_bmap_version(dev):
    ret = bose_get(0x00, 0x01)
    return ''.join([chr(b) for b in ret])

def get_function_blocks(dev):
    ret = bose_get(0x00, 0x02)
    return ret

def get_product_id(dev):
    ret = bose_get(0x00, 0x03)
    return format(ret[0] * 256 + ret[1], '04x'), ret[2]

def get_firmware_version(dev):
    ret = bose_get(0x00, 0x05)
    return ''.join([chr(b) for b in ret])

def get_mac_address(dev):
    ret = bose_get(0x00, 0x06)
    return ':'.join(
        map(lambda x: format(x, '02x'), ret)
    )

def get_serial_number(dev):
    ret = bose_get(0x00, 0x07)
    return ''.join([chr(b) for b in ret])

def get_product_name(dev):
    ret = bose_get(0x01, 0x02)
    return ''.join([chr(b) for b in ret[1:]])

def get_paired_devices(dev):
    ret = bose_get(0x04, 0x04)

    num_connected = ret[1]
    devices = [bytes(ret[2+i*6:8+i*6]) for i in range((len(ret) - 1) // 6)]

    return devices

# print(get_function_blocks(dev))

print('')
print('Product info')
print('------------')
print('BMAP version:     ', get_bmap_version(dev))
print('Function blocks:  ', get_function_blocks(dev))
print('Product id:       ', get_product_id(dev))
print('Firmware version: ', get_firmware_version(dev))
print('MAC address:      ', get_mac_address(dev))
print('Serial number:    ', get_serial_number(dev))
print('')
print('Settings')
print('--------')
print('FB Info:          ', '.'.join(map(chr, bose_get(0x01, 0x00))))
print('Product name:     ', get_product_name(dev))
print('Prompt language:  ', parse_prompt_language(bose_get(0x01, 0x03)))
print('Auto off:         ', bose_get(0x01, 0x04))
cnc = bose_get(0x01, 0x05)
print('CNC:              ', { 'unknown': cnc[0], 'anc': 10-cnc[1], 'unknown2': cnc[2] })
#print('ANR:              ', bose_get(0x01, 0x06))
print('Bass:             ', parse_bass(bose_get(0x01, 0x07)))


print('Buttons:          ', bose_get(0x01, 0x09))
print('Multipoint:       ', bose_get(0x01, 0x0A))
print('Side tone:        ', bose_get(0x01, 0x0B))
print('')
print('Status')
print('------')
print('FB Info:          ', '.'.join(map(chr, bose_get(0x02, 0x00))))
print('Battery level:    ', bose_get(0x02, 0x02))
print('AUX:              ', bose_get(0x02, 0x03))
print('Charger:          ', bose_get(0x02, 0x05))
print('')
print('Audio management')
print('----------------')
print('Source:           ', bose_get(0x05, 0x01))
print('')
print('Device management')
print('-----------------')
print('Paired devices:   ', list(map(lambda x: x.hex(), get_paired_devices(dev))))

# dev.ctrl_transfer(0x21, 9, 0x0200, 0, bytes([0x0c, 0x00, 0x04, 0x04, 0x04, 0x01]))

