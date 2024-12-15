import numpy as np


def generate_rho(SG_cRGB, option):
    # generate RGB polynomial martrix from original RGB data
    Rho_3 = SG_cRGB
    if option == 3:
        return Rho_3
    elif option == 5:
        Rho_5 = np.zeros((Rho_3.shape[0], Rho_3.shape[1] + 2))
        Rho_5[:, 0] = 1
        Rho_5[:, 1] = np.prod(Rho_3, axis=1)
        Rho_5[:, 2:] = Rho_3
        return Rho_5
    elif option == 9:
        Rho_9 = np.zeros((Rho_3.shape[0], Rho_3.shape[1] + 6))
        Rho_9[:, :3] = Rho_3
        Rho_9[:, 3] = Rho_3[:, 0] * Rho_3[:, 1]
        Rho_9[:, 4] = Rho_3[:, 0] * Rho_3[:, 2]
        Rho_9[:, 5] = Rho_3[:, 1] * Rho_3[:, 2]
        Rho_9[:, 6:] = Rho_3**2
        return Rho_9
    elif option == 11:
        Rho_5 = generate_rho(SG_cRGB, 5)
        Rho_9 = generate_rho(SG_cRGB, 9)
        Rho_11 = np.zeros((Rho_3.shape[0], Rho_3.shape[1] + 8))
        Rho_11[:, :2] = Rho_5[:, :2]
        Rho_11[:, 2:] = Rho_9
        return Rho_11
    elif option == 18:
        Rho_9 = generate_rho(SG_cRGB, 9)
        Rho_18 = np.zeros((Rho_3.shape[0], Rho_3.shape[1] + 15))
        Rho_18[:, :9] = Rho_9
        Rho_18[:, 9] = Rho_3[:, 0] * Rho_3[:, 1] ** 2
        Rho_18[:, 10] = Rho_3[:, 0] * Rho_3[:, 2] ** 2
        Rho_18[:, 11] = Rho_3[:, 1] * Rho_3[:, 0] ** 2
        Rho_18[:, 12] = Rho_3[:, 1] * Rho_3[:, 2] ** 2
        Rho_18[:, 13] = Rho_3[:, 2] * Rho_3[:, 0] ** 2
        Rho_18[:, 14] = Rho_3[:, 2] * Rho_3[:, 1] ** 2
        Rho_18[:, 15:] = Rho_3**3
        return Rho_18
    elif option == 20:
        Rho_5 = generate_rho(SG_cRGB, 5)
        Rho_18 = generate_rho(SG_cRGB, 18)
        Rho_20 = np.zeros((Rho_3.shape[0], Rho_3.shape[1] + 17))
        Rho_20[:, :2] = Rho_5[:, :2]
        Rho_20[:, 2:] = Rho_18
        return Rho_20
    else:
        raise ValueError("Invalid option")


def raw_to_xyz(raw, ccm):
    # Convert raw image to XYZ, XYZ=RGB@CCM
    RGB = raw.reshape(-1, 3)
    RGB_rho = generate_rho(RGB, ccm.shape[0])
    XYZ = RGB_rho @ ccm
    XYZ = XYZ.reshape(raw.shape)
    return XYZ