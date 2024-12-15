import numpy as np

class RawToRgb:
    def __init__(self, raw_data, bayer_pattern, demosaic=False, bit_depth=12):
        """
        Initialize the RawToRgb module.

        Parameters:
        - raw_data (np.ndarray): RAW image data (H x W).
        - bayer_pattern (np.ndarray): Bayer Pattern layout (e.g., [[0, 1], [3, 2]] for RGGB or [[2, 3], [1, 0]] for BGGR).
        - demosaic (bool): Whether to apply demosaicing. Default is False.
        - bit_depth (int): Bit depth of the RAW image (e.g., 10, 12, 14). Default is 12.
        """
        self.raw_data = raw_data
        self.bayer_pattern = bayer_pattern
        self.demosaic = demosaic
        self.bit_depth = bit_depth

    def process(self):
        """
        Process the RAW image to Camera RGB.

        Returns:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].
        """
        # Step 1: Normalize the RAW data to [0, 1] based on bit_depth
        max_value = 2 ** self.bit_depth - 1
        bayer_data = self.raw_data.astype(np.float32) / max_value

        # Step 2: Convert RAW to Camera RGB
        if self.demosaic:
            # Apply basic bilinear demosaicing
            rgb_data = self._demosaic_bilinear(bayer_data, self.bayer_pattern)
        else:
            # No demosaic: Directly map RAW to RGB
            rgb_data = self._no_demosaic(bayer_data, self.bayer_pattern)

        return rgb_data

    def _no_demosaic(self, bayer_data, bayer_pattern):
        """
        Directly map RAW data to RGB without demosaicing, reducing the image dimensions by half.

        Parameters:
        - bayer_data (np.ndarray): Bayer Pattern data (H x W), normalized to [0, 1].
        - bayer_pattern (np.ndarray): Bayer Pattern layout (e.g., [[0, 1], [3, 2]]).

        Returns:
        - rgb_data (np.ndarray): Camera RGB image (H/2 x W/2 x 3), normalized to [0, 1].
        """
        # Create an empty RGB image (H/2 x W/2 x 3)
        height, width = bayer_data.shape
        rgb_data = np.zeros((height // 2, width // 2, 3), dtype=np.float32)

        # Map Bayer Pattern to RGB channels, reducing dimensions by half
        if np.array_equal(bayer_pattern, [[0, 1], [3, 2]]):  # RGGB
            # R channel
            rgb_data[0::1, 0::1, 0] = bayer_data[0::2, 0::2]  # R

            # G channel (average the two green values)
            rgb_data[0::1, 0::1, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2]) / 2  # Average G1 and G2

            # B channel
            rgb_data[0::1, 0::1, 2] = bayer_data[1::2, 1::2]  # B

        elif np.array_equal(bayer_pattern, [[2, 3], [1, 0]]):  # BGGR
            # B channel
            rgb_data[0::1, 0::1, 2] = bayer_data[0::2, 0::2]  # B

            # G channel (average the two green values)
            rgb_data[0::1, 0::1, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2]) / 2  # Average G1 and G2

            # R channel
            rgb_data[0::1, 0::1, 0] = bayer_data[1::2, 1::2]  # R

        else:
            raise ValueError("Unsupported Bayer Pattern")

        return rgb_data

    def _demosaic_bilinear(self, bayer_data, bayer_pattern):
        """
        Apply basic bilinear demosaicing to interpolate missing color values.

        Parameters:
        - bayer_data (np.ndarray): Bayer Pattern data (H x W), normalized to [0, 1].
        - bayer_pattern (tuple): Bayer Pattern layout (e.g., RGGB, BGGR).

        Returns:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].
        """
        # Create an empty RGB image (H x W x 3)
        height, width = bayer_data.shape
        rgb_data = np.zeros((height, width, 3), dtype=np.float32)

        # Perform bilinear interpolation for each channel
        if np.array_equal(bayer_pattern, [[0, 1], [3, 2]]):  # RGGB
            # R channel
            rgb_data[0::2, 0::2, 0] = bayer_data[0::2, 0::2]
            rgb_data[0::2, 1::2, 0] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[0::2, 2::2], ((0, 0), (0, 1)), mode='edge')) / 2
            rgb_data[1::2, 0::2, 0] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[2::2, 0::2], ((0, 1), (0, 0)), mode='edge')) / 2
            rgb_data[1::2, 1::2, 0] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[0::2, 2::2], ((0, 0), (0, 1)), mode='edge') +
                                    np.pad(bayer_data[2::2, 0::2], ((0, 1), (0, 0)), mode='edge') + np.pad(bayer_data[2::2, 2::2], ((0, 1), (0, 1)), mode='edge')) / 4

            # G channel
            rgb_data[0::2, 1::2, 1] = bayer_data[0::2, 1::2]
            rgb_data[1::2, 0::2, 1] = bayer_data[1::2, 0::2]
            rgb_data[0::2, 0::2, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2]) / 2
            rgb_data[1::2, 1::2, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2] +
                                    np.pad(bayer_data[0::2, 3::2], ((0, 0), (0, 1)), mode='edge') + np.pad(bayer_data[3::2, 0::2], ((0, 1), (0, 0)), mode='edge')) / 4

            # B channel
            rgb_data[1::2, 1::2, 2] = bayer_data[1::2, 1::2]
            rgb_data[0::2, 1::2, 2] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[1::2, 3::2], ((0, 0), (0, 1)), mode='edge')) / 2
            rgb_data[1::2, 0::2, 2] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[3::2, 1::2], ((0, 1), (0, 0)), mode='edge')) / 2
            rgb_data[0::2, 0::2, 2] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[1::2, 3::2], ((0, 0), (0, 1)), mode='edge') +
                                  np.pad(bayer_data[3::2, 1::2], ((0, 1), (0, 0)), mode='edge') + np.pad(bayer_data[3::2, 3::2], ((0, 1), (0, 1)), mode='edge')) / 4

        elif np.array_equal(bayer_pattern, [[2, 3], [1, 0]]):  # BGGR
                # B channel
            rgb_data[0::2, 0::2, 2] = bayer_data[0::2, 0::2]
            rgb_data[0::2, 1::2, 2] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[0::2, 2::2], ((0, 0), (0, 1)), mode='edge')) / 2
            rgb_data[1::2, 0::2, 2] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[2::2, 0::2], ((0, 1), (0, 0)), mode='edge')) / 2
            rgb_data[1::2, 1::2, 2] = (bayer_data[0::2, 0::2] + np.pad(bayer_data[0::2, 2::2], ((0, 0), (0, 1)), mode='edge') +
                                    np.pad(bayer_data[2::2, 0::2], ((0, 1), (0, 0)), mode='edge') + np.pad(bayer_data[2::2, 2::2], ((0, 1), (0, 1)), mode='edge')) / 4

            # G channel
            rgb_data[0::2, 1::2, 1] = bayer_data[0::2, 1::2]
            rgb_data[1::2, 0::2, 1] = bayer_data[1::2, 0::2]
            rgb_data[0::2, 0::2, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2]) / 2
            rgb_data[1::2, 1::2, 1] = (bayer_data[0::2, 1::2] + bayer_data[1::2, 0::2] +
                                    np.pad(bayer_data[0::2, 3::2], ((0, 0), (0, 1)), mode='edge') + np.pad(bayer_data[3::2, 0::2], ((0, 1), (0, 0)), mode='edge')) / 4

            # R channel
            rgb_data[1::2, 1::2, 0] = bayer_data[1::2, 1::2]
            rgb_data[0::2, 1::2, 0] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[1::2, 3::2], ((0, 0), (0, 1)), mode='edge')) / 2
            rgb_data[1::2, 0::2, 0] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[3::2, 1::2], ((0, 1), (0, 0)), mode='edge')) / 2
            rgb_data[0::2, 0::2, 0] = (bayer_data[1::2, 1::2] + np.pad(bayer_data[1::2, 3::2], ((0, 0), (0, 1)), mode='edge') +
                                    np.pad(bayer_data[3::2, 1::2], ((0, 1), (0, 0)), mode='edge') + np.pad(bayer_data[3::2, 3::2], ((0, 1), (0, 1)), mode='edge')) / 4


        else:
            raise ValueError("Unsupported Bayer Pattern")

        return rgb_data