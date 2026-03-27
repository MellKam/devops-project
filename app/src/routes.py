from flask import Blueprint, jsonify
from . import db
from .models import Product

bp = Blueprint("main", __name__)

@bp.route("/health/live")
def liveness():
    return jsonify({"status": "ok"})

@bp.route("/health/ready")
def readiness():
    try:
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "ready", "db": True})
    except Exception:
        return jsonify({"status": "unavailable", "db": False}), 503

@bp.route("/api/products")
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@bp.route("/api/products/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(product.to_dict())
