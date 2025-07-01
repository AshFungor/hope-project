import pytest
import datetime

import sqlalchemy as orm

from typing import Generator
from dataclasses import dataclass

from app.codegen.hope import Request, Response
from app.codegen.prefecture import (
    AllPrefecturesRequest,
    UpdateLinkRequest,
)
from app.context import AppContext
from app.models import Prefecture, BankAccount, User, Company, Sex


@dataclass
class PrefectureFixture:
    prefecture: Prefecture
    prefecture_account: BankAccount
    user: User
    company: Company
    user_account: BankAccount
    company_account: BankAccount


@pytest.fixture
def prefecture_data() -> Generator[PrefectureFixture, None, None]:
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        PREFECTURE_ACCOUNT_ID = 1000
        USER_ACCOUNT_ID = 1111
        COMPANY_ACCOUNT_ID = 2222

        prefecture_account = BankAccount(id=PREFECTURE_ACCOUNT_ID)
        prefecture = Prefecture(name="TestPref", bank_account_id=PREFECTURE_ACCOUNT_ID)

        user_account = BankAccount(id=USER_ACCOUNT_ID)
        user = User(
            bank_account_id=USER_ACCOUNT_ID,
            prefecture_id=None,
            name="test",
            last_name="test",
            patronymic="test",
            login="tester",
            password="1234",
            sex=Sex.MALE,
            bonus=0,
            birthday=datetime.date(2000, 1, 1)
        )

        company_account = BankAccount(id=COMPANY_ACCOUNT_ID)
        company = Company(
            bank_account_id=COMPANY_ACCOUNT_ID,
            prefecture_id=PREFECTURE_ACCOUNT_ID,
            name="TestCompany",
            about="A test company for fixtures"
        )

        session.add_all([
            prefecture_account,
            prefecture,
            user_account,
            user,
            company_account,
            company,
        ])
        session.commit()

        yield PrefectureFixture(
            prefecture=prefecture,
            prefecture_account=prefecture_account,
            user=user,
            company=company,
            user_account=user_account,
            company_account=company_account
        )

        session.execute(orm.delete(Prefecture))
        session.execute(orm.delete(BankAccount))
        session.execute(orm.delete(User))
        session.execute(orm.delete(Company))
        session.commit()


def test_get_all_prefectures(client, prefecture_data: PrefectureFixture, logged_in_admin):
    req = Request(all_prefectures=AllPrefecturesRequest())
    resp = client.post("/api/prefecture/all", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert len(r.all_prefectures.prefectures) >= 1
    assert any(p.name == "TestPref" for p in r.all_prefectures.prefectures)


def test_update_link_not_found(client, prefecture_data: PrefectureFixture, logged_in_admin):
    req = Request(update_prefecture_link=UpdateLinkRequest(
        bank_account_id=999999,
        prefecture_id=1
    ))

    resp = client.post("/api/prefecture/link/update", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.update_prefecture_link.success is False
