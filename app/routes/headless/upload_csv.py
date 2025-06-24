# import datetime
# import io
# import logging

# import flask
# import pandas as pd
# import sqlalchemy as orm

# import app.models as models
# import app.modules.database.static as static
# import app.routes.blueprints as blueprints
# from app.env import env


# def parse(payload: bytes) -> pd.DataFrame | flask.Response:
#     frame = pd.read_csv(io.StringIO(payload.decode("UTF-8")), index_col=0)
#     if frame.isnull().any(axis=None):
#         logging.warning(f"received unparsed objects: \n{frame}")
#         return flask.Response(status=443)
#     return frame


# @blueprints.csv.route("/upload/csv/users", methods=["POST"])
# def parse_users():
#     result = parse(flask.request.data)
#     if isinstance(result, flask.Response):
#         return result
#     added = static.StaticTablesHandler.prepare_users(result)
#     if isinstance(added, str):
#         return flask.Response(added, status=443)
#     env.db.impl().session.commit()
#     return flask.Response(status=200)


# @blueprints.csv.route("/upload/csv/prefectures", methods=["POST"])
# def parse_prefectures():
#     result = parse(flask.request.data)
#     if isinstance(result, flask.Response):
#         return result
#     added = static.StaticTablesHandler.prepare_prefectures(result)
#     if isinstance(added, str):
#         return flask.Response(added, status=443)
#     env.db.impl().session.commit()
#     return flask.Response(status=200)


# @blueprints.csv.route("/upload/csv/cities", methods=["POST"])
# def parse_cities():
#     result = parse(flask.request.data)
#     if isinstance(result, flask.Response):
#         return result
#     added = static.StaticTablesHandler.prepare_cities(result)
#     if isinstance(added, str):
#         return flask.Response(added, status=443)
#     env.db.impl().session.commit()
#     return flask.Response(status=200)


# @blueprints.csv.route("/upload/csv/products", methods=["POST"])
# def parse_products():
#     result = parse(flask.request.data)
#     if isinstance(result, flask.Response):
#         return result
#     added = static.StaticTablesHandler.prepare_products(result)
#     if isinstance(added, str):
#         return flask.Response(added, status=443)
#     env.db.impl().session.commit()
#     return flask.Response(status=200)


# @blueprints.csv.route("/lol_kek", methods=["GET"])
# def lol_kek_azaza():
#     upper = datetime.datetime(year=2024, month=7, day=4, hour=9, minute=35)
#     down = datetime.datetime(year=2024, month=7, day=4, hour=9, minute=40)

#     consumed = (
#         env.db.impl()
#         .session.query(models.Product2BankAccount, models.Consumption)
#         .join(models.Product2BankAccount, models.Product2BankAccount.bank_account_id == models.Consumption.bank_account_id)
#         .filter(
#             orm.and_(
#                 models.Product2BankAccount.product_id == 1,
#                 models.Consumption.product_id == 36,
#                 models.Consumption.consumed_at > down,
#                 models.Consumption.consumed_at < upper,
#             )
#         )
#         .all()
#     )

#     for account, consume in consumed:
#         account.count += consume.count * 200
#         env.db.impl().session.delete(consume)

#     env.db.impl().session.commit()
#     return flask.Response(status=200)
