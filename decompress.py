#
# Logo.img extractor for Xiaomi Pad 5 (nabu)
#
#    .
#   /|\    While it is completely safe to extract the logo.img from your device, caution should
#  /_._\   be exercised when attempting to replace the logo, since it's currently untested.
#
# Status: Check README.md on how to get logo.img from your device.
#

import gzip
import struct
import os
import io
import shutil

# name of the image you want to read data from
input_file = "logo.img"

# Explicitly read image size from BMP header instead of using hard-coded offsets
# May be useful if you try to use this tool with another device's logo.bin, no difference
# if you use it with Xiaomi Pad 5 (nabu) images.
trim = False

# Step 1: Separate gzip archive
with open(input_file, "rb") as full_file, open("temp.gz", "wb") as out:
    full_file.seek(0x5000)
    out.write(full_file.read())

# Step 2: Extract logos from gzip archive
with gzip.GzipFile("temp.gz", mode="rb") as gz_in, open('uncompressed.bin', 'wb') as f_out:
    shutil.copyfileobj(gz_in, f_out)

os.remove("temp.gz")


# Step 3: Separate bitmaps from the uncompressed binary file
offsets = [0, 0xBB8038, 0x177006E, 0x23280A6]

with open("uncompressed.bin", "rb") as f_in:
    i = 1
    for offset in offsets:
        f_in.seek(offset)
        size = 0xBB8038
        if trim:
            f_in.seek(offset + 2)
            size = int.from_bytes(f_in.read(4), "little")
            if i+1 < len(offsets) - 1:
                offsets[i+1] = offsets[i]+size
            f_in.seek(offset)
        with open("logo_" + str(i) + ".bmp", "wb") as logo_f:
            print("Saving logo_" + str(i) + ".bmp")
            logo_f.write(f_in.read(size))
        i += 1

os.remove("uncompressed.bin")
