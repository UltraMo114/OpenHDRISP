Here’s the updated `README.md` for your project, **OpenHDRISP**, incorporating all the details you provided:

---

# OpenHDRISP: RAW to SDR/HDR Image Signal Processor

## Overview
**OpenHDRISP** is a lightweight and flexible Image Signal Processor (ISP) designed to convert RAW images into Standard Dynamic Range (SDR) or High Dynamic Range (HDR) images. It implements a complete pipeline from RAW data processing to SDR/HDR image generation, including black level correction, demosaicing, and color space transformations.

## Features
- **Black Level Correction (BLC)**: Corrects sensor black level offsets for accurate color representation.
- **Demosaicing**: Converts Bayer-pattern RAW data into full-color RGB images.
- **Two RAW-to-XYZ Conversion Methods**:
  - **AWB + CCM**: Automatic White Balance (AWB) followed by Color Correction Matrix (CCM).
  - **Direct Characterization Model**: A model-based approach for direct RAW-to-XYZ conversion.
- **XYZ to SDR/HDR Processing**: Converts XYZ color space data into SDR or HDR images using advanced tone mapping and gamma correction.
- **HDR Support**: Generates HDR images using the `Pillow-HEIF` library.

## Requirements
- Python 3.11.0
- Dependencies:
  ```
  contourpy==1.3.1
  cycler==0.12.1
  ExifRead==3.0.0
  fonttools==4.55.3
  kiwisolver==1.4.7
  matplotlib==3.10.0
  numpy==2.2.0
  packaging==24.2
  piexif==1.1.3
  pillow==11.0.0
  pillow_heif==0.21.0
  pyparsing==3.2.0
  python-dateutil==2.9.0.post0
  rawpy==0.23.2
  six==1.17.0
  ```

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/UltraMo114/OpenHDRISP.git
   cd OpenHDRISP
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Below is an example of how to use **OpenHDRISP** to process a RAW image into an SDR image:

```python
import rawpy
import numpy as np
import exifread
import math
from modules.RawBlc import RawBlc
from modules.RawToRgb import RawToRgb
from modules.RgbToXyz import RgbToXyz
from modules.XyzToRgb import XyzToRgb
from modules.RgbToImg import RgbToImg

# Path to the RAW file
raw_file_path = "DSC04657.dng"

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

# Step 2: Read RAW data using rawpy
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
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
