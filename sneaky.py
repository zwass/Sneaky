import sys

import Image

def int_to_bin_str(number, width=8):
    """Convert number to a binary string with width equal to width"""
    binstr = bin(number)[2:] # convert to binary and chop leading '0b'
    formatted = "{:0>{width}}".format(binstr, width=width) # add 0 padding
    return formatted

class MessageTooLargeError(Exception):
    pass

class ImgEncoder:
    """Class for encoding and decoding messages in images"""

    def __init__(self, img):
        """Initialize the encoder with an image"""
        self.img = img

    def _modify_sum(self, pix_r, bit):
        return pix_r + bit

    def _modify_parity(self, pix_r, bit):
        if bit == 0:
            return pix_r & ~1
        else:
            return pix_r | 1

    def encode(self, msg, parity):
        """Encodes the image with the message"""
        method = self._modify_sum
        if parity:
            method = self._modify_parity
        # pixel accessor
        pix = self.img.load()
        width, height = self.img.size
        if width * height < len(msg) * 8:
            raise MessageTooLargeError

        # make bit list for offsets
        bits = [int_to_bin_str(ord(x)) for x in msg]
        bitstring = "".join(bits)
        bitvals = [int(x) for x in bitstring]

        if parity:
            # This is so that the decode method encounters a
            # null byte and stops.
            bitvals.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

        for index, bit in enumerate(bitvals):
            x = index / height
            y = index % height
            # add to the red value
            pix[x,y] = (method(pix[x,y][0], bit), pix[x,y][1], pix[x,y][2])

    def decode(self, orig_img, parity):
        """Takes an original image, and returns the decoded message"""
        orig_pix = None
        if not parity:
            orig_pix = orig_img.load()
        enc_pix = self.img.load()

        width, height = self.img.size

        mod_8 = 7
        current_char = 0
        text = ""
        for index in range(width * height):
            x = index / height
            y = index % height
            if parity:
                secret_bit = enc_pix[x, y][0] & 1
                current_char += (secret_bit << mod_8)
            else:
                secret_bit = enc_pix[x, y][0] - orig_pix[x, y][0]
                current_char += (secret_bit << mod_8)
            if mod_8 == 0:
                char = chr(current_char)
                text += char
                if char == '\0':
                    break
                current_char, mod_8 = 0, 7
            else:
                mod_8 -= 1
        return text
        """
        charbin = ""
        msg = ""
        for index in range(width * height):
            x = index / height
            y = index % height
            charbin += str(enc_pix[x, y][0] - orig_pix[x, y][0])
            if len(charbin) == 8:
                char = chr(int(charbin, 2))
                if char == '\0':
                    break
                msg += char
                charbin = ""
        return msg
        """

    def save(self, outfile):
        """Save the image as a .png file"""
        self.img.save(outfile, "PNG")

def main_decode(encoded_img, out_file):
    print 'decoding...'
    decoder = ImgEncoder(Image.open(encoded_img))
    with open(out_file, 'wb') as f:
        f.write(decoder.decode(None, True))

def main_encode(plain_img, out_img, in_txt):
    print 'encoding...'
    img = Image.open(plain_img)
    encoder = ImgEncoder(img.copy())
    encoder.encode(open(in_txt).read(), True)
    print 'saving...'
    encoder.save(out_img)

def print_usage():
    print 'USAGE: python sneaky.py encode plain_img out_img in_txt'
    print '       python sneaky.py decode encoded_img out_file'
    sys.exit(1)

if __name__ == "__main__":
    argv = sys.argv
    if len(argv) > 5 or len(argv) < 4:
        print_usage()
    if argv[1] == 'encode':
        if len(argv) != 5:
            print_usage()
        main_encode(argv[2], argv[3], argv[4])
    elif argv[1] == 'decode':
        if len(argv) != 4:
            print_usage()
        main_decode(argv[2], argv[3])
    else:
        print_usage()
