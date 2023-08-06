# Function to compute BSA based on height (m) and weight (kg) using five methods

from math import sqrt

def BSA(weight: float, height: float, method="DuBois", digits=2) -> float:
    """Compute BSA

    Args:
        weight (float): weight in kg
        height (float): height in cm
        method (str): method to compute bsa choose between ['DuBois', 'Mosteller', 'Haycock', 'GehanGeorge', 'Fujimoto']
        digits (int, optional): Round the result. Defaults to 2.

    Returns:
        float: Body Surface Area values (unit: meters squared)
    """

    if method == "DuBois":
        bsa = 0.007184*weight**0.425 * height**0.725
    elif method == "Mosteller":
        bsa = sqrt(weight*height/3600)
    elif method == 'GehanGeorge':
        bsa = 0.0235 * weight**0.51456 * height**0.42246
    elif method == "Haycock":
        bsa = 0.024265 * weight**0.5378 * height**0.3964
    elif method == "Fujimoto":
        bsa = 0.008883 * weight**0.444 * height**0.663
    else:
        raise ValueError("Method should be one of thoses ['DuBois', 'Mosteller', 'Haycock', 'GehanGeorge', 'Fujimoto']")
    
    return round(bsa, digits)



# print(BSA(60, 170, "DuBois"))
# print(BSA(60, 170, "Mosteller"))
# print(BSA(60, 170, "Haycock"))
# print(BSA(60, 170, "GehanGeorge"))
# print(BSA(60, 170, "Fujimoto"))