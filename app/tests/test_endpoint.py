def test_liveness(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"

def test_readiness(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["db"] is True

def test_get_products_returns_list(client, app):
    from src import db
    from src.models import Product
    with app.app_context():
        db.session.add(Product(name="Iphone 13", price=599.99))
        db.session.commit()

    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Iphone 13"
    assert data[0]["price"] == 599.99

def test_get_product_by_id(client, app):
    from src import db
    from src.models import Product
    with app.app_context():
        db.session.add(Product(name="Samsung Galaxy S21", price=499.99))
        db.session.commit()

    response = client.get("/api/products/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["name"] == "Samsung Galaxy S21"

def test_get_product_not_found(client):
    response = client.get("/api/products/999")
    assert response.status_code == 404
