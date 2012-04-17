import sys

import Image

def int_to_bin_str(number, width=8):
    """Convert number to a binary string with width equal to width"""
    binstr = bin(number)[2:] #convert to binary and chop leading '0b'
    formatted = "{:0>{width}}".format(binstr, width=width) #add 0 padding
    return formatted

class ImgEncoder:
    """Class for encoding and decoding messages in images"""

    def __init__(self, img):
        """Initialize the encoder with an image"""
        self.img = img

    def encode(self, msg):
        """Encodes the image with the message"""
        #pixel accessor
        pix = self.img.load()
        width, height = self.img.size

        #make bit list for offsets
        bits = [int_to_bin_str(ord(x)) for x in msg]
        bitstring = "".join(bits)
        bitvals = [int(x) for x in bitstring]

        for index, bit in enumerate(bitvals):
            x = index / height
            y = index % height
            #add to the red channel
            pix[x,y] = (pix[0,index][0] + bit, pix[0,index][1], pix[0,index][2])


    def decode(self, orig_img):
        """Takes an original image, and returns the decoded message"""
        orig_pix = orig_img.load()
        enc_pix = self.img.load()

        width, height = self.img.size

        charbin = ""
        msg = ""
        for index in range(width*height):
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

    def save(self, outfile):
        """Save the image as a .bmp file"""
        self.img.save(outfile, "BMP")

def main(infile, outfile, msg):
    orig_img = Image.open(infile)
    encoder = ImgEncoder(orig_img.copy())
    encoder.encode(msg)
    encoder.save(outfile)
    print encoder.decode(orig_img)

if __name__ == "__main__":
    argv = sys.argv
    main(argv[1], argv[2], " ".join(argv[3:]))