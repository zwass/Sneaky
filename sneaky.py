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
            pix[x,y] = (pix[x,y][0] + bit, pix[x,y][1], pix[x,y][2])


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

def main(inimgfile, outimgfile, intxt, outtxt):
    orig_img = Image.open(inimgfile)
    encoder = ImgEncoder(orig_img.copy())
    encoder.encode(open(intxt).read())
    encoder.save(outimgfile)
    #print encoder.decode(orig_img)

if __name__ == "__main__":
    argv = sys.argv
    main(argv[1], argv[2], argv[3], argv[4])