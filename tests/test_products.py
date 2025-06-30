import pytest
import sqlalchemy as orm

from app.codegen.hope import Request, Response
from app.codegen.product import (
    AllProductsRequest,
    AvailableProductsRequest,
    ConsumeProductRequest,
    ConsumeProductResponseStatus,
    CreateProductRequest,
    ProductCountsRequest,
)
from app.codegen.types import Product
from app.context import AppContext


@pytest.fixture
def product_data():
    from app.models import BankAccount, Product, Product2BankAccount

    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        account = BankAccount(id=123)
        # number 1 is money and should be skipped for normal products
        money = Product(name="money", category="MONEY", level=2)
        product1 = Product(name="Laptop", category="TECHNIC", level=2)
        product2 = Product(name="Food", category="FOOD", level=1)

        link = Product2BankAccount(product_id=2, bank_account_id=123, count=5)

        session.add_all([money, product1, product2, link, account])
        session.commit()

        yield

        session.execute(orm.delete(Product2BankAccount))
        session.execute(orm.delete(Product))
        session.execute(orm.delete(BankAccount))
        session.commit()


def test_all_products(client, product_data, logged_in_normal):
    req = Request(all_products=AllProductsRequest())
    resp = client.post("/api/products/all", data=bytes(req))

    assert resp.status_code == 200

    r = Response().parse(resp.data)
    names = [p.name for p in r.all_products.products]
    assert "Laptop" in names
    assert "Food" in names


def test_available_products(client, product_data, logged_in_normal):
    req = Request(available_products=AvailableProductsRequest(bank_account_id=123))
    resp = client.post("/api/products/available", data=bytes(req))

    assert resp.status_code == 200

    r = Response().parse(resp.data)
    names = [p.name for p in r.available_products.products]
    assert "Laptop" in names


def test_product_counts(client, product_data):
    req = Request(product_counts=ProductCountsRequest(bank_account_id=123))
    resp = client.post("/api/products/counts", data=bytes(req))

    assert resp.status_code == 200

    r = Response().parse(resp.data)
    counts = {p.product.name: p.count for p in r.product_counts.products}
    assert counts["Laptop"] == 5


def test_consume_product_ok(client, product_data):
    req = Request(consume_product=ConsumeProductRequest(product="Laptop", bank_account_id=123))
    resp = client.post("/api/products/consume", data=bytes(req))

    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.consume_product.status == ConsumeProductResponseStatus.OK


def test_consume_product_not_enough(client, product_data):
    req = Request(consume_product=ConsumeProductRequest(product="Laptop", bank_account_id=9999))
    resp = client.post("/api/products/consume", data=bytes(req))

    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.consume_product.status == ConsumeProductResponseStatus.NOT_ENOUGH


def test_create_product_ok(client, logged_in_admin, product_data):
    req = Request(create_product=CreateProductRequest(product=Product(name="hello", category="FOOD", level=1)))

    resp = client.post("/api/products/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_product.status is True


def test_create_product_duplicate(client, logged_in_admin, product_data):
    req = Request(create_product=CreateProductRequest(product=Product(name="hello", category="FOOD", level=1)))

    for _ in range(2):
        resp = client.post("/api/products/create", data=bytes(req))
        assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_product.status is False
