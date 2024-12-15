import rawpy
import numpy as np
import exifread
import math
from modules.RawBlc import RawBlc
from modules.RawToRgb import RawToRgb
from modules.RgbToXyz import RgbToXyz
from modules.XyzToRgb import XyzToRgb
from modules.RgbToImg import RgbToImg
import matplotlib.pyplot as plt

# Path to the RAW file
raw_file_path = "MCCC.dng"

# Step 1: Read EXIF metadata
with open(raw_file_path, 'rb') as f:
    tags = exifread.process_file(f)

    # Extract relevant metadata
    shutter_speed = tags.get('EXIF ShutterSpeedValue')
    aperture = tags.get('EXIF ApertureValue')
    iso = tags.get('EXIF ISOSpeedRatings')

    # Print metadata
    print(f"Shutter Speed: {shutter_speed}")
    print(f"Aperture: {aperture}")
    print(f"ISO: {iso}")

# # Step 2: Read RAW data using rawpy
# with rawpy.imread(raw_file_path) as raw:

raw = rawpy.imread(raw_file_path)
# Extract RAW data, Bayer Pattern, and bit depth
raw_data = raw.raw_image  # RAW data (H x W)
bayer_pattern = raw.raw_pattern  # Bayer Pattern (e.g., [[0, 1], [3, 2]] for RGGB)
bit_depth = math.log(raw.white_level + 1, 2)   # Bit depth of the RAW data
blc_param = raw.black_level_per_channel[0]  # Black level per channel (R, G1, G2, B)
# Step 3: Apply Black Level Correction (BLC)
blc_params = {
    "R": blc_param,  # Black level offset for R channel
    "G1": blc_param,  # Black level offset for G1 channel
    "G2": blc_param,  # Black level offset for G2 channel
    "B": blc_param   # Black level offset for B channel
}
raw_blc = RawBlc(bayer_pattern, blc_params)
blc_data = raw_blc.process(raw_data)

# Step 4: Convert RAW to RGB
raw_to_rgb = RawToRgb(blc_data, bayer_pattern, demosaic=True, bit_depth=bit_depth)
rgb_data = raw_to_rgb.process()

# Step 5: Convert RGB to XYZ
ccm = np.array([
    [0.4124, 0.3576, 0.1805],
    [0.2126, 0.7152, 0.0722],
    [0.0193, 0.1192, 0.9505]
])
rgb_to_xyz = RgbToXyz(method="greyworld", ccm=ccm)
xyz_data = rgb_to_xyz.process(rgb_data)

# Step 6: Convert XYZ to RGB
xyz_to_rgb = XyzToRgb(method="default", color_space="sRGB")
rgb_data_final = xyz_to_rgb.process(xyz_data)

# Step 7: Save the final RGB image as a JPEG
rgb_to_img = RgbToImg(mode="SDR")
output_path = "output_sdr_default_gamma.jpeg"
rgb_to_img.process(rgb_data_final, output_path)
print(f"SDR image saved to {output_path}")

# # Optional: Display the final RGB image
# plt.imshow(rgb_data_final)
# plt.show()