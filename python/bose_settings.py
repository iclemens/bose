import struct

from bose_proto import bose_get, OPERATOR_SETGET

BOSE_LANGUAGES = {
    0: 'English UK',
    1: 'English US',
    2: 'French',
    3: 'Italian',
    4: 'German',
    5: 'Spanish ES',
    6: 'Spanish MX',
    7: 'Portuguese BR',
    8: 'Mandarin',
    9: 'Korean',
    10: 'Russian',
    11: 'Polish',
    12: 'Hebrew',
    13: 'Turkish',
    14: 'Dutch',
    15: 'Japanese',
    16: 'Cantonese',
    17: 'Arabic',
    18: 'Swedish',
    19: 'Danish',
    20: 'Norwegian',
    21: 'Finish'
}

def parse_prompt_language(data):
    unknown = data[0] & 0x80 == 0x80
    is_active = data[0] & 0x20 == 0x20

    language_id = data[0] & 0x1F
    language_name = BOSE_LANGUAGES[language_id]

    supported = []
    supported_mask = struct.unpack('>I', data[1:5])[0]
    for i in range(24):
        is_supported = supported_mask & (1 << i)
        if is_supported:
            supported.append({
                'id': i,
                'name': BOSE_LANGUAGES[i]
            })

    return {
        'prompts_active': is_active,
        'current_language': {
            'id': language_id,
            'name': language_name
        },
        'supported_languages': supported
    }

def get_prompt_language(transport):
    return parse_prompt_language(bose_get(transport, 0x01, 0x03))

def set_prompt_language(transport, prompts, language_id):
    payload = language_id
    if prompts:
        payload |= 0x20
    request = [0x01, 0x03, OPERATOR_SETGET, 0x01, payload]
    transport.send(request)

def set_noise_canelling(transport, level):
    request = [0x01, 0x05, OPERATOR_SETGET, 0x02, (10-level) if level else 0, level is not None]
    transport.send(request)