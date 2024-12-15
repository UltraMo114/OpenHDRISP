import numpy as np

class RawBlc:
    def __init__(self, bayer_pattern, blc_params):
        """
        Initialize the RawBlc module.

        Parameters:
        - bayer_pattern (np.ndarray): Bayer Pattern layout (e.g., [[0, 1], [3, 2]] for RGGB or [[2, 3], [1, 0]] for BGGR).
        - blc_params (dict): Black Level Correction parameters for each Bayer Pattern channel.
                             Example: {"R": 64, "G1": 64, "G2": 64, "B": 64}
        """
        self.bayer_pattern = bayer_pattern
        self.blc_params = blc_params

    def process(self, raw_data):
        """
        Process the RAW data with Black Level Correction.

        Parameters:
        - raw_data (np.ndarray): RAW image data (M x N).

        Returns:
        - blc_data (np.ndarray): Black Level Corrected RAW image data (M x N).
        """
        # Create a copy of the RAW data for correction
        blc_data = raw_data.copy()

        # Apply Black Level Correction based on the Bayer Pattern
        if np.array_equal(self.bayer_pattern, [[0, 1], [3, 2]]):  # RGGB
            # Apply BLC for RGGB pattern
            blc_data[0::2, 0::2] -= self.blc_params["R"]  # R channel
            blc_data[0::2, 1::2] -= self.blc_params["G1"]  # G1 channel
            blc_data[1::2, 0::2] -= self.blc_params["G2"]  # G2 channel
            blc_data[1::2, 1::2] -= self.blc_params["B"]  # B channel

        elif np.array_equal(self.bayer_pattern, [[2, 3], [1, 0]]):  # BGGR
            # Apply BLC for BGGR pattern
            blc_data[0::2, 0::2] -= self.blc_params["B"]  # B channel
            blc_data[0::2, 1::2] -= self.blc_params["G1"]  # G1 channel
            blc_data[1::2, 0::2] -= self.blc_params["G2"]  # G2 channel
            blc_data[1::2, 1::2] -= self.blc_params["R"]  # R channel

        else:
            raise ValueError("Unsupported Bayer Pattern")

        # Clip values to ensure non-negative values
        blc_data = np.clip(blc_data, 0, None)

        return blc_data