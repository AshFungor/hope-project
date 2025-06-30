import pytest
import sqlalchemy as orm
from datetime import datetime

from app.context import AppContext
from app.codegen.hope import Request, Response
from app.codegen.transaction import (
    CreateProductTransactionRequest,
    CreateMoneyTransactionRequest,
    CurrentTransactionsRequest,
    ViewTransactionsRequest,
    DecideOnTransactionRequest,
)
from app.codegen.types import TransactionStatusReason
from app.models import Product, BankAccount, Transaction, TransactionStatus, Product2BankAccount


@pytest.fixture
def tx_data():
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        money = Product(name="money", category="MONEY", level=1)
        product = Product(name="Laptop", category="TECHNIC", level=2)

        seller = BankAccount(id=1)
        buyer = BankAccount(id=2)

        money_link1 = Product2BankAccount(
            bank_account_id=1,
            product_id=1,
            count=1
        )
        money_link2 = Product2BankAccount(
            bank_account_id=2,
            product_id=1,
            count=1
        )
        product_link = Product2BankAccount(
            bank_account_id=1,
            product_id=2,
            count=1
        )

        session.add_all([
            money,
            product,
            seller,
            buyer,
            money_link1,
            money_link2,
            product_link
        ])
        session.commit()

        yield

        session.execute(orm.delete(Transaction))
        session.execute(orm.delete(Product))
        session.execute(orm.delete(BankAccount))
        session.execute(orm.delete(Product2BankAccount))
        session.commit()


def test_create_product_tx(client, tx_data, logged_in_normal):
    req = Request(
        create_product_transaction=CreateProductTransactionRequest(
            product="Laptop",
            customer_account=2,
            seller_account=1,
            count=1,
            amount=100
        )
    )
    resp = client.post("/api/transaction/product/create", data=bytes(req))
    assert resp.status_code == 200
    r = Response().parse(resp.data)
    assert r.create_transaction.status == TransactionStatusReason.OK


def test_create_money_tx(client, tx_data, logged_in_normal):
    req = Request(
        create_money_transaction=CreateMoneyTransactionRequest(
            customer_account=2,
            seller_account=1,
            amount=1
        )
    )
    resp = client.post("/api/transaction/money/create", data=bytes(req))
    assert resp.status_code == 200
    r = Response().parse(resp.data)
    assert r.create_transaction.status == TransactionStatusReason.OK


def test_current_tx(client, tx_data, logged_in_normal):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        tx = Transaction(
            product_id=2,
            customer_bank_account_id=2,
            seller_bank_account_id=1,
            count=1,
            amount=100,
            status=TransactionStatus.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            comment="test",
        )
        ctx.database.session.add(tx)
        ctx.database.session.commit()

    req = Request(current_transactions=CurrentTransactionsRequest(account=2))
    resp = client.post("/api/transaction/current", data=bytes(req))
    assert resp.status_code == 200
    r = Response().parse(resp.data)
    assert len(r.current_transactions.transactions) == 1


def test_view_tx_history(client, tx_data):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        tx = Transaction(
            product_id=2,
            customer_bank_account_id=2,
            seller_bank_account_id=1,
            count=1,
            amount=100,
            status=TransactionStatus.ACCEPTED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            comment="test",
        )
        ctx.database.session.add(tx)
        ctx.database.session.commit()

    req = Request(view_transaction_history=ViewTransactionsRequest(account=2))
    resp = client.post("/api/transaction/history", data=bytes(req))
    assert resp.status_code == 200
    r = Response().parse(resp.data)
    assert len(r.view_transaction_history.transactions) == 1


def test_decide_tx(client, tx_data, logged_in_normal):
    create_req = Request(
        create_product_transaction=CreateProductTransactionRequest(
            product="Laptop",
            customer_account=2,
            seller_account=1,
            count=1,
            amount=1
        )
    )
    create_resp = client.post("/api/transaction/product/create", data=bytes(create_req))
    assert create_resp.status_code == 200

    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        tx = ctx.database.session.execute(
            orm.select(Transaction).filter_by(customer_bank_account_id=2)
        ).scalar_one()

    decide_req = Request(
        decide_on_transaction=DecideOnTransactionRequest(
            id=tx.id,
            status="accepted"
        )
    )
    decide_resp = client.post("/api/transaction/decide", data=bytes(decide_req))
    assert decide_resp.status_code == 200

    r = Response().parse(decide_resp.data)
    assert r.decide_on_transaction.status == TransactionStatusReason.OK

