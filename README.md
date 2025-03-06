# How to extract and replace boot logo on Xiaomi Pad 5 (nabu)

When your tablet starts up, it displays a Xiaomi Mi and "Powered by android" logo. This project attempts to study how the logo is stored and potentially how to replace it.

Warning: This project is a work in progress and we haven't verified if logo replacement is actually possible. Please do not attempt to replace the logo unless you are willing to potentially brick your device and have the tools to reflash the device if you do end up bricking it!

## Extraction

Xiaomi Pad 5 stores it's boot logo on the imagefv partition. You can retrieve it by first entering `adb shell` on a rooted device, then enter the following command:

`su -c dd if=/dev/block/by-name/imagefv_a of=/sdcard/imagefv_a.img` for A slot

`su -c dd if=/dev/block/by-name/imagefv_a of=/sdcard/imagefv_a.img` for B slot

Note: Please double check that that **if** points to the block device, NOT **of**!

Then you can **exit** the ADB shell and pull each file with the following commands:

`adb pull /sdcard/imagefv_a.img` for A slot

`adb pull /sdcard/imagefv_b.img` for B slot

Next you have to download something called UEFITool. You can find it [here](https://github.com/LongSoft/UEFITool/releases). Make sure you download the one labelled "UEFITool" and not something else.

Extract the downloaded ZIP archive and run the executable it contains.

Next in UEFITool, open one of the extracted imagefv files (File > Open image file...). Make sure file type "All files (*)" is selected, otherwise you won't see the extracted imagefv.img file.

Once opened, click on the small triangle next to "UEFI image", then another triange next to "EfiFirmwareFileSystem2Guid".

Find the following GUID: B90FFA41-D22C-4B0E-AC8B-65B98ACE057D

It should have a UI section and Raw section. UI section should have a text "logo.img".

Right click on the Raw section and select "Extract body...". This will let you save the image file. Set the file type to all files and call it "logo.img". Make sure you save it to the same location as decompress.py.

Now run the decompress.py script, which will then allow you to retrieve all 4 splash images. They'll be saved as logo_1 (normal startup), logo_2 (fastboot), logo_3 (unlocked bootloader) and logo_4 (destroyed device). You can now view and edit them with a regular photo editing program.

## Repacking

Important: All BMP files must be saved in 24-bit color depth and they must be uncompressed. Do not use RLE! Verify that the modified BMPs are the exact same size as the originals.

Once you have made modifications to the bitmaps, you can create a modified image by running the compress.py script.

This will create a logo_new.img file, which you can use for repacking and ultimately replacing the boot splash.

I will not go into how to use UEFITool to repack the modified logo.img into imagefv, since it's potentially dangerous and I'm not confident in the exact steps you'd need to take myself.

I tried flashing a modified image to splash partition (which is empty normally and there is no logo partition), but it doesn't seem to work unfortunately, so the only way seems to be to modify imagefv partition directly.