from Crypto.PublicKey import RSA
import Image
import sys

KEY_SIZE = 1024
MAX_BITS = 127

def int_to_bin_str(number, width):
    """Convert number to a binary string with width equal to width"""
    binstr = bin(number)[2:] # convert to binary and chop leading '0b'
    formatted = "{:0>{width}}".format(binstr, width=width) # add 0 padding
    return formatted

def _encrypt(chunk, pub_key):
    cipher = pub_key.encrypt(chunk, None)[0]
    size = KEY_SIZE / 8
    if len(cipher) < size:
        # pad
        return '\0' * (size - len(cipher)) + cipher
    return cipher

def encrypt(path, pub_key):
    text = None
    with open(path, 'rU') as f:
        text = f.read()

    chunks = []
    for lower in range(0, len(text), MAX_BITS):
        upper = lower + MAX_BITS
        chunks.append(text[lower:upper])
    return [_encrypt(chunk, pub_key) for chunk in chunks]

class MessageTooLargeError(Exception):
    pass

class ImgEncoder:
    """Class for encoding and decoding messages in images"""

    def __init__(self, img):
        """Initialize the encoder with an image"""
        self.img = img

    def encode(self, msg_file, pub_key):
        """Encodes the image with the message"""
        ciphertext = encrypt(msg_file, pub_key)
        num_chunks = [int(b) for b in int_to_bin_str(len(ciphertext), 32)]
        ciphertext = ''.join(ciphertext)

        # pixel accessor
        pix = self.img.load()
        width, height = self.img.size
        if width * height < len(ciphertext) * 8 + 32:
            raise MessageTooLargeError

        for index, bit in enumerate(num_chunks):
            x = index / height
            y = index % height
            # modify the red value
            pix_r = pix[x,y][0]
            if bit:
                pix_r |= 1
            else:
                pix_r &= ~1
            pix[x,y] = (pix_r, pix[x,y][1], pix[x,y][2])
            
        # make bit list for offsets
        bits = [int_to_bin_str(ord(x), 8) for x in ciphertext]
        bitstring = "".join(bits)
        bitvals = [int(x) for x in bitstring]

        for bit in bitvals:
            index += 1
            x = index / height
            y = index % height
            # modify the red value
            pix_r = pix[x,y][0]
            if bit:
                pix_r |= 1
            else:
                pix_r &= ~1
            pix[x,y] = (pix_r, pix[x,y][1], pix[x,y][2])

    def decode(self, priv_key):
        enc_pix = self.img.load()

        width, height = self.img.size
        
        num_chunks = 0
        for index in range(32):
            num_chunks <<= 1
            x = index / height
            y = index % height
            if enc_pix[x, y][0] & 1:
                num_chunks += 1

        index = 32
        size = KEY_SIZE
        plain_chunks = []
        for _ in range(num_chunks):
            chunk = ''
            mod_8 = 0
            byte = 0
            for _ in range(size):
                x = index / height
                y = index % height
                byte <<= 1
                byte += enc_pix[x, y][0] & 1
                if mod_8 == 7:
                    chunk += chr(byte)
                    mod_8 = 0
                    byte = 0
                else:
                    mod_8 += 1
                index += 1
            plain_chunks.append(priv_key.decrypt(chunk))
        return ''.join(plain_chunks)
                
    def save(self, outfile):
        """Save the image as a .bmp file"""
        self.img.save(outfile, "BMP")

def main_decode(encoded_img, out_file, priv_key):
    print 'decoding...'
    decoder = ImgEncoder(Image.open(encoded_img))
    plaintext = decoder.decode(priv_key)
    print 'saving...'
    with open(out_file, 'wb') as f:
        f.write(plaintext)

def main_encode(plain_img, out_img, in_txt, pub_key):
    print 'encoding...'
    encoder = ImgEncoder(Image.open(plain_img))
    encoder.encode(in_txt, pub_key)
    print 'saving...'
    encoder.save(out_img)

def print_usage():
    print 'USAGE: python watermark.py encode plain_img out_img in_txt pub_key'
    print '       python watermark.py decode encoded_img out_file priv_key'
    sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 6 or len(argv) < 5:
        print_usage()
    if argv[1] == 'encode':
        if len(argv) != 6:
            print_usage()
        public = None
        try:
            with open(argv[5], 'rU') as pubfile:
                public = RSA.importKey(pubfile.read())
        except (ValueError, IndexError, TypeError):
            print 'invalid public key file'
            sys.exit(1)
        main_encode(argv[2], argv[3], argv[4], public)
    elif argv[1] == 'decode':
        if len(argv) != 5:
            print_usage()
        private = None
        try:
            with open(argv[4], 'rU') as privfile:
                private = RSA.importKey(privfile.read())
        except (ValueError, IndexError, TypeError):
            print 'invalid public key file'
            sys.exit(1)
        main_decode(argv[2], argv[3], private)
    else:
        print_usage()
