OPERATOR_SET = 0x00
OPERATOR_GET = 0x01
OPERATOR_SETGET = 0x02
OPERATOR_STATUS = 0x03
OPERATOR_ERROR = 0x04
OPERATOR_START = 0x05

BOSE_ERROR_MESSAGES = {
    1: 'Invalid length',
    2: 'Invalid checksum',
    3: 'Function block not supported',
    4: 'Function not supported',
    5: 'Operator not supported for function',
    6: 'Invalid data',
    7: 'Requested data is not available',
    8: 'Runtime error',
    9: 'Timeout',
    10: 'Invalid state',
    11: 'Device not found',
    12: 'Busy',
    13: 'Failed to connect, timeout',
    14: 'Failed to connect, no key',
    15: 'OTA already in progress',
    16: 'OTA low battery',
    17: 'OTA no charger',
    -1: 'Function specific error'
}

def bose_get(transport, block, func):
    request = [block, func, OPERATOR_GET, 0x00]
    transport.send(request)

    res = transport.recv()

    if res[0] != block:
        raise RuntimeError(f'Requested block {block:02x}, received {res[0]:02x}')
    if res[1] != func:
        print(res)
        raise RuntimeError(f'Requested function {func:02x}, received {res[1]:02x}')

    # Raise an exception on error
    if res[2] == OPERATOR_ERROR:
        if res[4] in BOSE_ERROR_MESSAGES:
            raise RuntimeError(BOSE_ERROR_MESSAGES[res[4]])
        raise RuntimeError(f'Unknown error, code: {res[4]:02x}')

    if res[2] != OPERATOR_STATUS:
        raise RuntimeError(f'Operator not supported: {res[3]:02x}.')

    len = res[3]
    return res[4:4+len]




