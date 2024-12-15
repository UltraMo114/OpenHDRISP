import numpy as np

class XyzToRgb:
    def __init__(self, method="default", display_matrix=None, color_space="sRGB"):
        """
        Initialize the XyzToRgb module.

        Parameters:
        - method (str): Method to use for conversion ("default" or "custom").
        - display_matrix (np.ndarray): Custom display matrix (3x3) for custom conversion.
        - color_space (str): Predefined color space for default conversion ("sRGB", "Display P3", "BT-2020").
        """
        self.method = method
        self.display_matrix = display_matrix  # Custom display matrix (3x3)
        self.color_space = color_space  # Predefined color space

        # Define default color space matrices (XYZ to RGB)
        self.color_space_matrices = {
            "sRGB": np.array([
                [3.2406, -1.5372, -0.4986],
                [-0.9689, 1.8758, 0.0415],
                [0.0557, -0.2040, 1.0570]
            ]),
            "Display P3": np.array([
                [2.4934, -1.0296, -0.4958],
                [-0.9314, 1.9082, 0.0239],
                [0.0358, -0.1486, 1.2483]
            ]),
            "BT-2020": np.array([
                [1.7167, -0.3557, -0.2534],
                [-0.6667, 1.6165, 0.0158],
                [0.0176, -0.0428, 0.9421]
            ])
        }

    def process(self, xyz_data):
        """
        Convert XYZ to RGB.

        Parameters:
        - xyz_data (np.ndarray): XYZ image (H x W x 3), normalized to [0, 1].

        Returns:
        - rgb_data (np.ndarray): RGB image (H x W x 3), normalized to [0, 1].
        """
        if self.method == "custom":
            return self._custom_matrix_transform(xyz_data)
        elif self.method == "default":
            return self._default_color_space_transform(xyz_data)
        else:
            raise ValueError(f"Unsupported method: {self.method}")

    def _custom_matrix_transform(self, xyz_data):
        """
        Convert XYZ to RGB using a custom display matrix.

        Parameters:
        - xyz_data (np.ndarray): XYZ image (H x W x 3), normalized to [0, 1].

        Returns:
        - rgb_data (np.ndarray): RGB image (H x W x 3), normalized to [0, 1].
        """
        # Reshape XYZ data for matrix multiplication
        height, width, _ = xyz_data.shape
        xyz_flat = xyz_data.reshape(-1, 3)  # Flatten to (N x 3)

        # Apply custom display matrix
        rgb_flat = np.dot(xyz_flat, self.display_matrix.T)

        # Reshape back to original dimensions
        rgb_data = rgb_flat.reshape(height, width, 3)

        # Clip values to [0, 1] to avoid overflow
        rgb_data = np.clip(rgb_data, 0, 1)

        return rgb_data

    def _default_color_space_transform(self, xyz_data):
        """
        Convert XYZ to RGB using a predefined color space.

        Parameters:
        - xyz_data (np.ndarray): XYZ image (H x W x 3), normalized to [0, 1].

        Returns:
        - rgb_data (np.ndarray): RGB image (H x W x 3), normalized to [0, 1].
        """
        # Get the color space matrix
        if self.color_space not in self.color_space_matrices:
            raise ValueError(f"Unsupported color space: {self.color_space}")

        color_space_matrix = self.color_space_matrices[self.color_space]

        # Reshape XYZ data for matrix multiplication
        height, width, _ = xyz_data.shape
        xyz_flat = xyz_data.reshape(-1, 3)  # Flatten to (N x 3)

        # Apply color space matrix
        rgb_flat = np.dot(xyz_flat, color_space_matrix.T)

        # Reshape back to original dimensions
        rgb_data = rgb_flat.reshape(height, width, 3)

        # Clip values to [0, 1] to avoid overflow
        rgb_data = np.clip(rgb_data, 0, 1)

        return rgb_data