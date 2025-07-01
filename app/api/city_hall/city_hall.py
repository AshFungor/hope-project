from sqlalchemy import select
from app.api import Blueprints

from app.context import AppContext
from app.models import CityHall as CityHallModel, User
from app.api.helpers import protobufify, pythonify

from app.codegen.hope import Response
from app.codegen.city import CityHallRequest, CityHallResponse
from app.codegen.types import CityHall as CityHallProto


@Blueprints.master.route("/api/city_hall", methods=["POST"])
@pythonify(CityHallRequest)
def get_city_hall(ctx: AppContext, req: CityHallRequest):
    session = ctx.database.session

    city_hall = session.execute(select(CityHallModel)).scalar_one_or_none()

    if not city_hall:
        return protobufify(Response(city_hall=CityHallResponse()))

    mayor = session.get(User, city_hall.mayor_id)
    economic_assistant = session.get(User, city_hall.economic_assistant_id)
    social_assistant = session.get(User, city_hall.social_assistant_id)

    city_hall_proto = CityHallProto(
        bank_account_id=city_hall.bank_account_id,
        mayor_account_id=mayor.bank_account_id if mayor else 0,
        economic_assistant_account_id=economic_assistant.bank_account_id if economic_assistant else 0,
        social_assistant_account_id=social_assistant.bank_account_id if social_assistant else 0,
    )

    return protobufify(Response(city_hall=CityHallResponse(city_hall=city_hall_proto)))