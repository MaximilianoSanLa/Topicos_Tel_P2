def calculate_total(price: float, quantity: int, delivery_cost: float = 0.0) -> float:
    """Calculate the total purchase cost."""
    return round(price * quantity + delivery_cost, 2)
