import numpy as np

class RgbToXyz:
    def __init__(self, method="greyworld", ccm=None, polynomial_coeffs=None, bit_depth=None, expo_factor=None):
        """
        Initialize the RgbToXyz module.

        Parameters:
        - method (str): Method to use for conversion ("greyworld" or "polynomial").
        - ccm (np.ndarray): Color Correction Matrix (3x3) for CCM-based conversion.
        - polynomial_coeffs (np.ndarray): Polynomial coefficients for polynomial-based conversion.
        """
        self.method = method
        self.ccm = ccm  # Color Correction Matrix (3x3)
        self.polynomial_coeffs = polynomial_coeffs  # Polynomial coefficients (1xN)
        self.bit_depth = bit_depth
        self.expo_factor = expo_factor

    def process(self, rgb_data):
        """
        Convert Camera RGB to XYZ.

        Parameters:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].

        Returns:
        - xyz_data (np.ndarray): XYZ image (H x W x 3).
        """
        if self.method == "greyworld":
            return self._greyworld_ccm(rgb_data)
        elif self.method == "polynomial":
            return self._polynomial_transform(rgb_data)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def _greyworld_ccm(self, rgb_data):
        """
        Convert Camera RGB to XYZ using greyworld white balance and CCM.

        Parameters:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].

        Returns:
        - xyz_data (np.ndarray): XYZ image (H x W x 3).
        """
        # Step 1: Apply greyworld white balance
        rgb_balanced = self._greyworld_white_balance(rgb_data)

        # Step 2: Convert white-balanced RGB to XYZ using CCM
        xyz_data = np.dot(rgb_balanced, self.ccm.T)

        return xyz_data

    def _greyworld_white_balance(self, rgb_data):
        """
        Apply greyworld white balance to the Camera RGB image.

        Parameters:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].

        Returns:
        - rgb_balanced (np.ndarray): White-balanced RGB image (H x W x 3).
        """
        # Calculate the mean values for each channel
        mean_r = np.mean(rgb_data[..., 0])
        mean_g = np.mean(rgb_data[..., 1])
        mean_b = np.mean(rgb_data[..., 2])

        # Calculate scaling factors for white balance
        scale_r = mean_g / mean_r
        scale_b = mean_g / mean_b

        # Apply white balance
        rgb_balanced = rgb_data.copy()
        rgb_balanced[..., 0] *= scale_r
        rgb_balanced[..., 2] *= scale_b

        # Clip values to [0, 1] to avoid overflow
        rgb_balanced = np.clip(rgb_balanced, 0, 1)

        return rgb_balanced

    def _polynomial_transform(self, rgb_data):
        """
        Convert Camera RGB to XYZ using a polynomial transformation.

        Parameters:
        - rgb_data (np.ndarray): Camera RGB image (H x W x 3), normalized to [0, 1].

        Returns:
        - xyz_data (np.ndarray): XYZ image (H x W x 3).
        """
        # Reshape RGB data for polynomial transformation
        height, width, _ = rgb_data.shape
        rgb_flat = rgb_data.reshape(-1, 3)  # Flatten to (N x 3)
        rgb_flat = rgb_flat * (2**self.bit_depth - 1)  # Scale to [0, 2^bit_depth - 1]
        # Polynomial expansion
        rgb_expanded = np.zeros((rgb_flat.shape[0], rgb_flat.shape[1] + 6))  # Expand to (N x 9)
        rgb_expanded[:, :3] = rgb_flat  # Copy original RGB values
        rgb_expanded[:, 3] = rgb_flat[:, 0] * rgb_flat[:, 1]  # R * G
        rgb_expanded[:, 4] = rgb_flat[:, 0] * rgb_flat[:, 2]  # R * B
        rgb_expanded[:, 5] = rgb_flat[:, 1] * rgb_flat[:, 2]  # G * B
        rgb_expanded[:, 6:] = rgb_flat**2  # R^2, G^2, B^2

        # Apply polynomial transformation using the coefficients
        xyz_flat = np.dot(rgb_expanded, self.polynomial_coeffs.T) * self.expo_factor / 10000  # (N x 3) for PQ curve for divisible by 10000

        # Reshape back to original dimensions
        xyz_data = xyz_flat.reshape(height, width, 3)

        return xyz_data