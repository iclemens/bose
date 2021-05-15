from os import read
import struct
import sys
import io


def read_partitions(fp):
    while True:
        type = fp.read(8).decode('utf8')

        if not type:
            break

        length = struct.unpack('>I', fp.read(4))[0]
        stream = io.BytesIO(fp.read(length))

        if type == 'PARTDATA':
            id = struct.unpack('>I', stream.read(4))[0]
        else:
            id = None

        yield type, id, stream



def parse_header(fp):
    header = {}
    while True:
        field = fp.read(1).decode('ASCII')

        if field == 'V':
            assert fp.read(2).decode('ASCII') == 'R:'
            version_tmp = (
                struct.unpack('b', fp.read(1))[0], 
                struct.unpack('b', fp.read(1))[0],
                struct.unpack('b', fp.read(1))[0],
                hex(struct.unpack('>I', fp.read(4))[0])
            )
            
            header['version'] = version_tmp
        elif field == 'C':
            assert fp.read(7).decode('ASCII') == "SRA6810"
            header['csra6810'] = fp.read(16)
        elif field == 'O':
            assert fp.read(7).decode('ASCII') == 'TP_PROD'
            header['opt_prod'] = fp.read(2)
        elif field == 'P':
            assert fp.read(7).decode('ASCII') == 'RODUCT:'
            header['product'] = fp.read(10)
        elif not field:
            break

    return header


if __name__ == '__main__':
    filename = sys.argv[1]

    with open(filename, 'rb') as fp:
        for type, id, stream in read_partitions(fp):
            if type == 'APPUHDR5':
                print("Header:")
                header = parse_header(stream)
                for field in header:
                    print(f"{field}:", header[field])
                print("")
            elif type == 'PARTDATA':
                print(f"Parition {id}")
                with open(f'part_{id}.dat', 'wb') as of:
                    of.write(stream.read())
            elif type == 'APPUPFTR':
                with open(f'footer.dat', 'wb') as of:
                    of.write(stream.read())
