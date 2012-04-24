Progress so far:

  - Installed Image library

  - Implemented two types of encoding
      1. Sum: The i'th bit to encode is added to the red value of the i'th
              pixel. To decode, you simply "subtract" the original image.
      2. Parity: The red value of the i'th pixel is made to share the parity
                 of the i'th bit to encode (by either adding or subtracting 1).
                 To decode, simply map (mod 2) over the red values. The
                 original image is not need.

  - Implemented a minor optimization to reduce string operations. Instead of
    using strings to build decoded characters, e.g. "01101010", integers were
    used instead, e.g. 106, and created using bitwise operations. This did
    not actually produce that much of a speedup, only about 10%.

So far nothing has really changed from our proposal.

Work Breakdown:

    Zach:
      General framework for encoding/decoding
      Sum coding
    Nick:
      Parity coding
      Optimizations
