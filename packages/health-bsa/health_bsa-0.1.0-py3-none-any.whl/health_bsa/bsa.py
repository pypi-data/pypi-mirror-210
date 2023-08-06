# Function to compute BSA based on height (m) and weight (kg)

def compute_bsa(weight: float, height: float, digits=2) -> float:
    """Compute BSA

    Args:
        weight (float): weight in kg
        height (float): height in cm
        digits (int, optional): Round the result. Defaults to 2.

    Returns:
        float: Body Surface Area values (unit: meters squared)
    """
    bsa = 0.007184*weight**0.425 * height**0.725
    return round(bsa, digits)

# print(compute_bsa(60, 180))
# print(help(compute_bsa))