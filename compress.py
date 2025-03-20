#
# Compressed logo.img generator for Xiaomi Pad 5 (nabu)
#
#    .
#   /|\    Replacing your device's logo.img requires modifying imagefv partition with UEFITool,
#  /_._\   which is risky and can brick your device if done incorrectly!
#
# Status: Will produce identical file to factory logo.img if default images are used. Logo
#         replacement may be possible, but currently no way of correctly modifying the contents
#         of imagefv.elf has been found.
#

import gzip
import struct
import time
import io
import shutil
import os

input_file = "logo" # Do not change!

# You may change these if you wish
output_file = "logo_generated.img"
logo_files = ["logo_1.bmp", "logo_2.bmp", "logo_3.bmp", "logo_4.bmp"]

# Get size of file stream
def GetSize(f):
    pos = f.tell()
    f.seek(0, io.SEEK_END)
    size = f.tell()
    f.seek(pos) # back to where we were
    return size

# Step 1: Concatenate BMP files
# - Logo 1 is displayed during normal startup (for a few seconds if bootloader is unlocked)
# - Logo 2 is displayed when the device is in fastboot mode (adb reboot bootloader)
# - Logo 3 is displayed during startup when the bootloader detects it has been unlocked
# - Logo 4 is displayed when secure boot fails (i.e. device is bricked)

with open(input_file, "wb") as combined_logo, open(logo_files[0], "rb") as startup_logo, open(logo_files[1], "rb") as fastboot_logo, open(logo_files[2], "rb") as unlocked_logo, open(logo_files[3], "rb") as bricked_logo:
    combined_logo.write(startup_logo.read())
    if GetSize(startup_logo) < 0xBB8038: combined_logo.write(bytearray(0xBB8038 - GetSize(startup_logo)))
    combined_logo.write(fastboot_logo.read())
    if GetSize(fastboot_logo) < 0xBB8038: combined_logo.write(bytearray(0xBB8038 - GetSize(fastboot_logo)))
    combined_logo.write(unlocked_logo.read())
    if GetSize(unlocked_logo) < 0xBB8038: combined_logo.write(bytearray(0xBB8038 - GetSize(unlocked_logo)))
    combined_logo.write(bricked_logo.read())
    if GetSize(bricked_logo) < 0xBB8038: combined_logo.write(bytearray(0xBB8038 - GetSize(bricked_logo)))

# The infamous "LOGO!!!!" magic followed by 8 unknown bytes
#   - SPECULATION: 19 00 00 00 may be an indication for BL that the images are compressed, the other 4 bytes could be memory buffer size?
# and then an alternating pattern of offsets and sizes (4 bytes each) for the decompressed bitmaps in little endian byte order
magic = b'LOGO!!!!\x19\x00\x00\x00u\x82\x01\x00\x00\x00\x00\x008\x80\xbb\x008\x80\xbb\x006\x80\xbb\x00n\x00w\x018\x80\xbb\x00\xa6\x802\x028\x80\xbb\x00'

# Step 2: Compress data into a buffer
# This will create a gzip archive that has the default header
with open(input_file, "rb") as f_in:
    compressed_buffer = io.BytesIO()
    
    with gzip.GzipFile(fileobj=compressed_buffer, mode="wb", compresslevel=9) as gz_out: # Xiaomi used Level 9 compression, so this is what we'll be doing as well
        shutil.copyfileobj(f_in, gz_out)

# Step 3: Extract the compressed data (removing gzip.GzipFile's default header)
# Prevents duplicate headers. Note: DO NOT change input_file variable, otherwise this part of the code will break!
compressed_data = compressed_buffer.getvalue()[10:]  # Skip the first 10 bytes (header)

with open(output_file, "wb") as f_out:
    # Step 4: Write header
    for i in range(1, 0x4001): f_out.write(b'\x00') # Zero pad 0x4000 bytes
    f_out.write(magic) # Write the magic we described earlier
    for i in range(1, 0x1001 - len(magic)): f_out.write(b'\x00') # Write another 1000 bytes of zero padding
    # Step 5: Write compressed bitmap data
    f_out.write(b'\x1f\x8b')  # Gzip magic number
    f_out.write(b'\x08')  # Compression method: Deflate
    f_out.write(b'\x00')  # Flags: No filename, no extra fields
    
    # IMPORTANT: This is the only part of the file that will be different compared to the original if you use original BMPs
    f_out.write(struct.pack("<L", int(time.time())))  # Modification time
    
    f_out.write(b'\x02')  # Extra flags: Maximum compression
    f_out.write(b'\xff')  # OS: Unknown

    # Write the compressed data (without the unwanted header)
    f_out.write(compressed_data)

    # Write additional padding (footer)
    for i in range(1, 0xD8C): f_out.write(b'\x00')

# delete unneeded logo file
os.remove("logo")
print("The operation has been completed successfully")