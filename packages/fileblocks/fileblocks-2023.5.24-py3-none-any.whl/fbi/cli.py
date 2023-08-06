import argparse
import concurrent.futures
import hashlib
import pathlib
import pybloomfilter
import requests
import sys
from blake3 import blake3
from fbi import __fbi__
from fbi import __version__
from tqdm.auto import tqdm

def calculate():

    BLOCKSIZE = 65536
    sha256_hasher = hashlib.sha256()
    with open(__fbi__, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            sha256_hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    f.close()
    sha256 = sha256_hasher.hexdigest().upper()
    return sha256

def download():

    if __fbi__.is_file() == False:
        print('UPDATING: '+str(__fbi__))
        getbloom()
        sha256 = verify()
        check = calculate()
        if check != sha256:
            print('CORRUPTED: '+str(__fbi__))
            sys.exit(1)
        else:
            print('VERIFIED: '+str(__fbi__))
    else:
        sha256 = verify()
        check = calculate()
        if check != sha256:
            print('UPDATING: '+str(__fbi__))
            getbloom()
            check = calculate()
            if check != sha256:
                print('CORRUPTED: '+str(__fbi__))
                sys.exit(1)
            else:
                print('VERIFIED: '+str(__fbi__))
        else:
            print('CURRENT: '+str(__fbi__))

def getbloom():

    r = requests.get('https://static.fileblock.info/fbi.bloom')
    if r.status_code == 200:
        with open(__fbi__, 'wb') as f:
            print('SUCCESS: https://static.fileblock.info/fbi.bloom')
            f.write(r.content)
    else:
        print('FAILED: https://static.fileblock.info/fbi.bloom')
        sys.exit(1)

def blocks(input, output):

    if __fbi__.is_file() == False:
        print('MISSING: '+str(__fbi__))
    else:
        offset = 0
        out = pathlib.Path(output).joinpath('fbi-'+pathlib.Path(input).name)
        size = pathlib.Path(input).stat().st_size
        fbi = pybloomfilter.BloomFilter.open(str(__fbi__))
        with open(out, 'w') as o:
            with open(input, 'rb') as f:
                for offset in tqdm(range(size)):
                    f.seek(offset)
                    data = f.read(512)
                    if not data:
                        break
                    b3 = blake3(data).hexdigest().upper()
                    if b3 == 'AF1349B9F5F9A1A6A0404DEA36DCC9499BCB25C9ADC112B7CC9A93CAE41F3262':
                        o.write(' ')
                        offset += 512
                    else:
                        if b3 not in fbi:  
                            try:
                                o.write(data[0:1].decode('utf-8'))
                            except UnicodeDecodeError:
                                o.write(data[0:1].decode('utf-8', 'ignore'))
                                pass
                            offset += 1
                        else:
                            offset += 512
            f.close()
        o.close()

def verify():

    r = requests.get('https://static.fileblock.info/fbi.sha256')
    if r.status_code == 200:
        print('SUCCESS: https://static.fileblock.info/fbi.sha256')
        return r.text
    else:
        print('FAILED: https://static.fileblock.info/fbi.sha256')
        sys.exit(1)

def main():

    parser = argparse.ArgumentParser(description='FBI - Walk the line, Byte by Byte Analysis')
    parser.add_argument('-b', '--blocks', help='Input Filename', required=False)
    parser.add_argument('-d', '--download', help='Download Bloom Filter', action='store_true')
    parser.add_argument('-o', '--output', help='Output Directory', required=False)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args = parser.parse_args()

    if args.download:
        download()
    elif args.blocks:
        if args.output:
            output = args.output
        else:
            output = pathlib.Path().absolute()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(blocks, args.blocks, output)
    else:
        print('USAGE: fbi -h')