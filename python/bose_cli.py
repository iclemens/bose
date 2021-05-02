import argparse

from bose_bt import BoseBT
from bose_proto import bose_get, OPERATOR_SETGET
from bose_settings import get_prompt_language, set_prompt_language, set_noise_canelling

def get_volume(transport):
    """Returns tuple with (maximum volume, current volume)"""

    res = bose_get(transport, 0x05, 0x05)
    return ( res[0], res[1] )

def set_volume(transport, volume):
    request = [0x05, 0x05, OPERATOR_SETGET, 0x01, volume]
    transport.send(request)
    return transport.recv()

def main():

    parser = argparse.ArgumentParser(description='Bose CLI utility')
    parser.add_argument('mode', type=str, nargs=1)
    parser.add_argument('--bluetooth', const='bluetooth', action='store_const')
    parser.add_argument('--volume', nargs=1, type=int)

    args = parser.parse_args()

    mode = args.mode[0]

    address = '4C:87:5D:A1:74:C1'
    bosebt = BoseBT(address)

    #print(get_prompt_language(bosebt))
    set_prompt_language(bosebt, False, 1)

main()
