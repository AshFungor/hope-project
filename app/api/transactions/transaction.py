import datetime
from http import HTTPStatus

import sqlalchemy as orm
from flask import Response
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import preprocess, protobufify, local_datetime
from app.api.transactions.processor import complete_transaction, process
from app.context import AppContext, function_context
from app.models import Product, Transaction, TransactionStatus
from app.models.queries import wrap_crud_context
from app.codegen.transaction import (
	CreateProductTransactionRequest,
	CreateMoneyTransactionRequest,
	CreateTransactionResponse,
	CreateTransactionResponseCreationStatus,
	ViewCurrentTransactionsRequest,
	CurrentTransactionEntry,
	CurrentTransactionsResponse,
	ViewHistoryRequest,
	TransactionEntry,
	ViewTransactionsResponse,
	DecideTransactionRequest,
	DecideTransactionResponse,
)
from app.codegen.transaction import TransactionEntry as EntryProto


@Blueprints.transactions.route("/api/transaction/product/create", methods=["POST"])
@login_required
@preprocess(CreateProductTransactionRequest)
@function_context
def new_proposal(ctx: AppContext, req: CreateProductTransactionRequest):
	products = ctx.database.session.execute(
		orm.select(Product).filter_by(name=req.product)
	).scalars().all()

	if len(products) != 1:
		return protobufify(
			CreateTransactionResponse(
				CreateTransactionResponseCreationStatus.MULTIPLE_PRODUCTS
			)
		)

	product = products[0]
	with wrap_crud_context():
		tx = Transaction(
			product.id,
			req.customer_account,
			req.seller_account,
			req.count,
			req.amount,
			TransactionStatus.CREATED,
			datetime.datetime.now(),
			datetime.datetime.now(),
			"",
		)
		ctx.database.session.add(tx)
		ctx.database.session.commit()

	return protobufify(
		CreateTransactionResponse(
			CreateTransactionResponseCreationStatus.OK
		)
	)


@Blueprints.transactions.route("/api/transaction/money/create", methods=["POST"])
@login_required
@preprocess(CreateMoneyTransactionRequest)
@function_context
def new_money_proposal(ctx: AppContext, req: CreateMoneyTransactionRequest):
	with wrap_crud_context():
		tx = Transaction(
			1,
			req.customer_account,
			req.seller_account,
			req.amount,
			req.amount,
			TransactionStatus.CREATED,
			datetime.datetime.now(),
			datetime.datetime.now(),
			"",
		)
		ctx.database.session.add(tx)
		message, ok = process(tx, is_money=True)

		if not ok:
			ctx.logger.warning(message)
			return Response(message, status=HTTPStatus.BAD_REQUEST)

		return protobufify(
			CreateTransactionResponse(
				CreateTransactionResponseCreationStatus.OK
			)
		)

	return "bad request", 406


@Blueprints.transactions.route("/api/transaction/view/current", methods=["POST"])
@login_required
@preprocess(ViewCurrentTransactionsRequest)
@function_context
def active_proposals(ctx: AppContext, req: ViewCurrentTransactionsRequest):
	entries = ctx.database.session.execute(
		orm.select(Transaction, Product)
		.filter(
			orm.and_(
				Transaction.status == TransactionStatus.CREATED,
				Transaction.customer_bank_account_id == req.account,
			)
		)
		.join(Product, Product.id == Transaction.product_id)
	).all()

	return protobufify(
		CurrentTransactionsResponse(
			transactions=[
				CurrentTransactionEntry(
					transaction_id=tx.id,
					amount=tx.amount,
					count=tx.count,
					product=product.name,
					second_side=tx.seller_bank_account_id,
				)
				for tx, product in entries
			]
		)
	)


@Blueprints.transactions.route("/api/transaction/view/history", methods=["POST"])
@preprocess(ViewHistoryRequest)
@function_context
def view_proposal_history(ctx: AppContext, req: ViewHistoryRequest):
	def fetch(for_seller: bool):
		column = Transaction.seller_bank_account_id if for_seller else Transaction.customer_bank_account_id
		return ctx.database.session.execute(
			orm.select(Transaction, Product)
			.filter(column == req.account)
			.join(Product, Product.id == Transaction.product_id)
		).all()

	response = []
	for group, role in [(fetch(True), "seller"), (fetch(False), "customer")]:
		for tx, product in group:
			response.append(
				TransactionEntry(
					transaction_id=tx.id,
					amount=tx.amount,
					count=tx.count,
					product=product.name,
					second_side=tx.customer_bank_account_id if role == "seller" else tx.seller_bank_account_id,
					status=EntryProto.Status(tx.status).value,
					updated_at=local_datetime(ctx, tx.updated_at).isoformat(),
					side=role,
					is_money=(product.id == 1),
				)
			)

	response.sort(key=lambda e: datetime.datetime.fromisoformat(e.updated_at), reverse=True)
	return protobufify(ViewTransactionsResponse(transactions=response))


@Blueprints.transactions.route("/api/transaction/decide", methods=["POST"])
@login_required
@preprocess(DecideTransactionRequest)
@function_context
def decide_on_proposal(ctx: AppContext, req: DecideTransactionRequest):
	message, ok = complete_transaction(req.account, req.status)
	ctx.logger.info(f"transaction {req.account} decision={req.status} success={ok}: {message}")

	if not ok:
		return Response(message, status=HTTPStatus.BAD_REQUEST)

	return protobufify(DecideTransactionResponse(status=DecideTransactionResponse.Status.OK))
