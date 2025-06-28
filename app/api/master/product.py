import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.context import AppContext
from app.models import Product as ProductModel
from app.models.queries import wrap_crud_context

from app.codegen.product import (
    CreateProductRequest,
    CreateProductResponse,
)


@Blueprints.master.route("/api/products/create", methods=["POST"])
@login_required
@pythonify(CreateProductRequest)
def create_product(ctx: AppContext, req: CreateProductRequest):
    with wrap_crud_context():
        exists = ctx.database.session.execute(
            orm.select(ProductModel).filter_by(name=req.product.name)
        ).scalar_one_or_none()

        if exists:
            return protobufify(CreateProductResponse(status=False))

        product = ProductModel(
            name=req.product.name,
            category=req.product.category,
            level=req.product.level,
        )
        ctx.database.session.add(product)
        ctx.database.session.commit()

        return protobufify(CreateProductResponse(status=True))
