from modules.RawToRgb import RawToRgb
from modules.RgbToXyz import RgbToXyz
from modules.XyzToRgb import XyzToRgb
from modules.RgbToImg import RgbToImg
import matplotlib.pyplot as plt
import numpy as np
import exifread

# Example usage of the RawToRgb module
raw_file_path = "MCCC.dng"

# 打开 RAW 文件
with open(raw_file_path, 'rb') as f:
    # 读取 EXIF 元数据
    tags = exifread.process_file(f)

    # 提取快门速度、光圈大小和 ISO
    shutter_speed = tags.get('EXIF ShutterSpeedValue')
    aperture = tags.get('EXIF ApertureValue')
    iso = tags.get('EXIF ISOSpeedRatings')

    # 打印结果
    print(f"Shutter Speed: {shutter_speed}")
    print(f"Aperture: {aperture}")
    print(f"ISO: {iso}")

# # Initialize the RawToRgb module (no demosaic)
raw_to_rgb = RawToRgb(raw_file_path, demosaic=False, bit_depth=14)
rgb_data_no_demosaic = raw_to_rgb.process()
# print("RGB data (no demosaic) shape:", rgb_data_no_demosaic.shape)
# plt.imshow(rgb_data_no_demosaic)
# plt.show()

# Define the Color Correction Matrix (CCM)
ccm = np.array([
    [0.4124, 0.3576, 0.1805],
    [0.2126, 0.7152, 0.0722],
    [0.0193, 0.1192, 0.9505]
])

# Initialize the RgbToXyz module with greyworld method
rgb_to_xyz = RgbToXyz(method="greyworld", ccm=ccm)


# Convert RGB to XYZ
xyz_data = rgb_to_xyz.process(rgb_data_no_demosaic)

xyz_to_rgb = XyzToRgb(method="default", color_space="sRGB")

rgb_data = xyz_to_rgb.process(xyz_data)
print(np.amax(rgb_data), np.amin(rgb_data))
plt.imshow(rgb_data)
plt.show()

rgb_to_img = RgbToImg(mode="SDR")

# Save the image as a 16-bit TIFF
output_path = "output_sdr_default_gamma.jpeg"
rgb_to_img.process(rgb_data, output_path)
print(f"SDR image saved to {output_path}")
# print("XYZ data shape:", xyz_data.shape)


# # 读取 .npy 文件
# data = np.load('ILCE7CM2_Ver2_D65.npy')

# # 打印读取的数据
# print(data.shape)