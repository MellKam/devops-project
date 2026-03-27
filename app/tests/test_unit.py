def test_product_to_dict():
    from src.models import Product
    p = Product(id=1, name="Iphone 13", price=599.99)
    assert p.to_dict() == {"id": 1, "name": "Iphone 13", "price": 599.99}
