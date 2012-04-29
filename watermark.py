"""A module for encrypting and watermarking images."""

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
    """Encrypts a chunk and pads it to 128 bytes"""
    cipher = pub_key.encrypt(chunk, None)[0]
    size = KEY_SIZE / 8
    if len(cipher) < size:
        # pad
        return '\0' * (size - len(cipher)) + cipher
    return cipher

def encrypt(path, pub_key):
    """Encrypts the contents of a file and returns a list of
    encrypted chunks."""
    text = None
    with open(path, 'rU') as f:
        text = f.read()

    # Chunk the file into segments of 127 bytes
    chunks = []
    for lower in range(0, len(text), MAX_BITS):
        upper = lower + MAX_BITS
        chunks.append(text[lower:upper])
    return [_encrypt(chunk, pub_key) for chunk in chunks]

class MessageTooLargeError(Exception):
    """Exception thrown when the message is too large for the image."""
    pass

class ImgEncoder:
    """Class for encoding and decoding messages in images"""

    def __init__(self, img):
        """Initialize the encoder with an image"""
        self.img = img

    def encode(self, msg_file, pub_key):
        """Encrypts the message and encodes it in the image."""
        ciphertext = encrypt(msg_file, pub_key)
        # Need to encode number of chunks for reading
        num_chunks = [int(b) for b in int_to_bin_str(len(ciphertext), 32)]
        ciphertext = ''.join(ciphertext)

        # Pixel accessor
        pix = self.img.load()
        width, height = self.img.size
        if width * height < len(ciphertext) * 8 + 32:
            raise MessageTooLargeError

        # Write the number of chunks to the image
        for index, bit in enumerate(num_chunks):
            x = index / height
            y = index % height
            # modify the red value's parity
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

        # Write the serialized ciphertext
        for bit in bitvals:
            index += 1
            x = index / height
            y = index % height
            # modify the red value's parity
            pix_r = pix[x,y][0]
            if bit:
                pix_r |= 1
            else:
                pix_r &= ~1
            pix[x,y] = (pix_r, pix[x,y][1], pix[x,y][2])

    def decode(self, priv_key):
        """Read the encrypted message from the image and decrypt it."""
        enc_pix = self.img.load()

        width, height = self.img.size
        
        # Read the number of chunks in the message
        num_chunks = 0
        for index in range(32):
            num_chunks <<= 1
            x = index / height
            y = index % height
            if enc_pix[x, y][0] & 1:
                num_chunks += 1

        index = 32
        plain_chunks = []
        # Iterate over chunks
        for _ in range(num_chunks):
            chunk = ''
            mod_8 = 0
            byte = 0
            # Create chunk
            for _ in range(KEY_SIZE):
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
            # Decrypt chunk
            plain_chunks.append(priv_key.decrypt(chunk))
        return ''.join(plain_chunks)
                
    def save(self, outfile):
        """Save the image as a .bmp file"""
        self.img.save(outfile, "BMP")

def main_decode(encoded_img, out_file, priv_key):
    """Decode the given image and write the result to the file."""
    print 'decoding...'
    decoder = ImgEncoder(Image.open(encoded_img))
    plaintext = decoder.decode(priv_key)
    print 'saving...'
    with open(out_file, 'wb') as f:
        f.write(plaintext)

def main_encode(plain_img, out_img, in_txt, pub_key):
    """Encode the given text on a copy of plain_img and write it to out_img.""" 
    print 'encoding...'
    encoder = ImgEncoder(Image.open(plain_img))
    encoder.encode(in_txt, pub_key)
    print 'saving...'
    encoder.save(out_img)

def get_key(keyfile):
    """Parses the key from the file."""
    try:
        with open(keyfile, 'rU') as keyf:
            return RSA.importKey(keyf.read())
    except (IOError, ValueError, IndexError, TypeError):
        print 'invalid public key file'
        sys.exit(1)

def print_usage():
    """Prints the usage"""
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
        public = get_key(argv[5])
        try:
            main_encode(argv[2], argv[3], argv[4], public)
        except:
            print 'Error encoding the message.'
    elif argv[1] == 'decode':
        if len(argv) != 5:
            print_usage()
        private = get_key(argv[4])
        try:
            main_decode(argv[2], argv[3], private)
        except:
            print 'Error decoding the message.'
    else:
        print_usage()
