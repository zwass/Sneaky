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
        """Save the image as a .bmp file"""
        self.img.save(outfile, "BMP")

def main(inimgfile, outimgfile, intxt, outtxt):
    orig_img = Image.open(inimgfile)
    encoder = ImgEncoder(orig_img.copy())
    print 'encoding...'
    encoder.encode(open(intxt).read(), True)
    print 'saving...'
    encoder.save(outimgfile)
    print 'decoding...'
    print encoder.decode(orig_img, True)

if __name__ == "__main__":
    argv = sys.argv
    main(argv[1], argv[2], argv[3], argv[4])
