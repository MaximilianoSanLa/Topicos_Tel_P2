def calculate_discount(price: float, discount: float) -> float:
    """Apply a percentage discount to a price."""
    return round(price * (1 - discount / 100), 2)
