import sys
import csv
import json
import os
sys.path.insert(0, "/app")

from src import create_app, db
from src.models import Product

OUTPUT_DIR = "/seed_output"

PRODUCTS = [
    {"name": "Iphone 13", "price": 599.99},
    {"name": "Samsung Galaxy S21", "price": 499.99},
    {"name": "Google Pixel 6", "price": 399.99},
    {"name": "OnePlus 9", "price": 429.99},
    {"name": "Sony Xperia 5 II", "price": 949.99}
]

app = create_app()
with app.app_context():
    if Product.query.count() == 0:
        for item in PRODUCTS:
            db.session.add(Product(**item))
        db.session.commit()
        print("Seeded 5 products.")
    else:
        print("Data already exists, skipping.")

    products = Product.query.all()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(f"{OUTPUT_DIR}/products.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "price"])
        writer.writeheader()
        writer.writerows([p.to_dict() for p in products])

    with open(f"{OUTPUT_DIR}/products.json", "w") as f:
        json.dump([p.to_dict() for p in products], f, indent=2)

    with open(f"{OUTPUT_DIR}/seed.log", "w") as f:
        f.write(f"Seeded {len(products)} products.\n")

    print("Seed output written to", OUTPUT_DIR)
