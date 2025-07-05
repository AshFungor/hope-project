from dataclasses import dataclass
from datetime import datetime

import pytest
import sqlalchemy as orm

from app.codegen.goal import (
    CreateGoalRequest,
    CreateGoalResponseStatus,
    GetLastGoalRequest,
)
from app.codegen.hope import Request, Response
from app.codegen.types import Goal as GoalProto
from app.context import AppContext, class_context
from app.models import BankAccount, Goal, Product, Product2BankAccount, User
from app.models.queries import CRUD
from tests.helpers.orm import TestCRUD


@dataclass
class GoalContext:
    account: BankAccount
    wallet: Product2BankAccount

    @class_context
    def __init__(self, ctx: AppContext):
        TestCRUD.create_money()
        user = TestCRUD.create_user()

        self.account = ctx.database.session.get(BankAccount, user.bank_account_id)
        self.wallet = CRUD.query_money(self.account.id)


@pytest.fixture(scope="module")
def goal_data():
    ctx = AppContext.safe_load()

    with ctx.app.app_context():
        yield GoalContext()

        # deleting by one does not work for some reason
        ctx.database.session.execute(orm.delete(Goal))
        ctx.database.session.execute(orm.delete(User))
        ctx.database.session.execute(orm.delete(BankAccount))
        ctx.database.session.execute(orm.delete(Product2BankAccount))
        ctx.database.session.commit()


def test_create_goal(client, goal_data, logged_in_normal):
    req = Request(create_goal=CreateGoalRequest(goal=GoalProto(bank_account_id=123, value=500)))
    resp = client.post("/api/goal/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_goal.status == CreateGoalResponseStatus.OK


def test_create_goal_exists(client, goal_data, logged_in_normal):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        goal = Goal(bank_account_id=123, value=500, amount_on_setup=1000)
        ctx.database.session.add(goal)
        ctx.database.session.commit()

    req = Request(create_goal=CreateGoalRequest(goal=GoalProto(bank_account_id=123, value=1000)))
    resp = client.post("/api/goal/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_goal.status == CreateGoalResponseStatus.EXISTS


def test_get_last_goal_none(client, goal_data, logged_in_normal):
    req = Request(last_goal=GetLastGoalRequest(bank_account_id=123))
    resp = client.post("/api/goal/get_last", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    # python better protos do not support optional yet, gotta
    # make skip this for now
    # assert r.last_goal.goal is None


def test_get_last_goal_exists(client, goal_data, logged_in_normal):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        goal = Goal(bank_account_id=123, value=1000, amount_on_setup=2000, created_at=datetime.now())
        ctx.database.session.add(goal)
        ctx.database.session.commit()

    req = Request(last_goal=GetLastGoalRequest(bank_account_id=123))
    resp = client.post("/api/goal/get_last", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.last_goal.goal is not None
    assert r.last_goal.goal.bank_account_id == 123
    assert r.last_goal.goal.value == 1000
