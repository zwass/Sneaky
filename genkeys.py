from Crypto.PublicKey import RSA
from Crypto import Random

import sys

KEY_SIZE = 1024

def print_usage():
    print 'USAGE: python genkeys.py pub_file priv_file'
    sys.exit(1)

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) != 3:
        print_usage()
    private = RSA.generate(KEY_SIZE, Random.new().read)
    public = private.publickey()
    with open(argv[1], 'w') as pubfile:
        pubfile.write(public.exportKey())
    with open(argv[2], 'w') as privfile:
        privfile.write(private.exportKey())
