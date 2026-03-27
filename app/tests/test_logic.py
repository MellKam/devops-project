def is_positive(price):
    return price > 0

def test_price_must_be_positive():
    assert is_positive(9.99) is True
    assert is_positive(-1) is False
    assert is_positive(0) is False
