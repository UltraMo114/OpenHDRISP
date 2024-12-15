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

class ImagePipeline:
    def __init__(self, params):
        self.params = params
        self.raw_data = None
        self.blc_data = None
        self.rgb_data = None
        self.xyz_data = None
        self.rgb_data_final = None
        self.exposure_factor = self.read_exif()

    def read_raw_data(self):
        raw = rawpy.imread(self.params["raw_file_path"])
        self.raw_data = raw.raw_image
        self.bayer_pattern = raw.raw_pattern
        self.bit_depth = math.log(raw.white_level + 1, 2)
        self.blc_params = {
            "R": raw.black_level_per_channel[0],
            "G1": raw.black_level_per_channel[1],
            "G2": raw.black_level_per_channel[2],
            "B": raw.black_level_per_channel[3]
        }

    def read_exif(self):
        tags = exifread.process_file(open(self.params["raw_file_path"], 'rb'))
        shutter_speed = tags['EXIF ExposureTime'].values[0]
        aperture = tags['EXIF FNumber'].values[0]
        ISO = tags['EXIF ISOSpeedRatings'].values[0]
        CCM_aperture, CCM_SS, CCM_ISO = 8, 1/4, 100
        expo_factor = (CCM_SS / shutter_speed) * (aperture / CCM_aperture)**2 * (CCM_ISO / ISO)
        return expo_factor

    def apply_blc(self):
        raw_blc = RawBlc(self.bayer_pattern, self.blc_params)
        self.blc_data = raw_blc.process(self.raw_data)

    def convert_raw_to_rgb(self):
        raw_to_rgb = RawToRgb(self.blc_data, self.bayer_pattern, demosaic=self.params["demosaic"], bit_depth=self.bit_depth)
        self.rgb_data = raw_to_rgb.process()

    def convert_rgb_to_xyz(self):
        rgb_to_xyz = RgbToXyz(method=self.params["rgb_to_xyz_method"], ccm=self.params["ccm"], polynomial_coeffs=self.params["polynomial_coeffs"], bit_depth=self.bit_depth, expo_factor=self.exposure_factor)
        self.xyz_data = rgb_to_xyz.process(self.rgb_data)

    def convert_xyz_to_rgb(self):
        xyz_to_rgb = XyzToRgb(method=self.params["xyz_to_rgb_method"], color_space=self.params["color_space"])
        self.rgb_data_final = xyz_to_rgb.process(self.xyz_data)

    def save_image(self):
        rgb_to_img = RgbToImg(mode=self.params["output_mode"], gamma=self.params["gamma"], color_space=self.params["color_space"], hdr_format= self.params["hdr_format"])
        rgb_to_img.process(self.rgb_data_final, self.params["output_path"])
        print(f"Image saved to {self.params['output_path']}")

    def run(self, steps):
        """
        根据传入的步骤列表运行流水线
        :param steps: 步骤名称的列表，例如 ["read_raw_data", "apply_blc", "convert_raw_to_rgb"]
        """
        for step in steps:
            if hasattr(self, step):
                getattr(self, step)()  # 动态调用方法
            else:
                raise ValueError(f"Unknown step: {step}")

def main():
    # Parameters dictionary
    params = {
        "raw_file_path": "MCCC.dng",
        "rgb_to_xyz_method": "polynomial", ## greyworld = AWB + CCM, polynomial = polynomial transform
        "xyz_to_rgb_method": "default",
        "color_space": "Display P3",
        "output_mode": "HDR",
        "image_name": "output_img",
        "hdr_format": "AVIF",
        "output_path": "output_img.avif",
        "ccm": np.array([
            [0.4124, 0.3576, 0.1805],
            [0.2126, 0.7152, 0.0722],
            [0.0193, 0.1192, 0.9505]
        ]),
        "gamma": 2.2,
        "demosaic": False,
        "polynomial_coeffs": np.load('ILCE7CM2_Ver2_D65.npy').T,
    }

    # Create an instance of the ImagePipeline class
    pipeline = ImagePipeline(params)

    # 定义需要运行的步骤
    steps = [
        "read_raw_data",
        "apply_blc",
        "convert_raw_to_rgb",
        "convert_rgb_to_xyz",
        "convert_xyz_to_rgb",
        "save_image"
    ]

    # 运行流水线
    pipeline.run(steps)

if __name__ == "__main__":
    main()