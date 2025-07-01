import sqlalchemy as orm
from flask_login import login_required

from app.api import Blueprints
from app.api.helpers import protobufify, pythonify
from app.codegen.hope import Response as Response
from app.codegen.product import CreateProductRequest, CreateProductResponse
from app.context import AppContext
from app.models import Product as ProductModel
from app.models.queries import wrap_crud_context


@Blueprints.master.route("/api/products/create", methods=["POST"])
@login_required
@pythonify(CreateProductRequest)
def create_product(ctx: AppContext, req: CreateProductRequest):
    with wrap_crud_context():
        existing = ctx.database.session.scalar(
            orm.select(ProductModel).filter_by(name=req.product.name)
        )

        if existing:
            return protobufify(
                Response(create_product=CreateProductResponse(status=False))
            )

        new_product = ProductModel(
            name=req.product.name,
            category=req.product.category,
            level=req.product.level,
        )

        ctx.database.session.add(new_product)
        ctx.database.session.commit()

        return protobufify(
            Response(create_product=CreateProductResponse(status=True))
        )
