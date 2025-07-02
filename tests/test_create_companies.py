import pytest
import sqlalchemy as orm
from datetime import datetime

from app.codegen.company import (
    CreateCompanyRequest,
    CreateCompanyResponseStatus,
    Founder,
)
from app.codegen.hope import Request, Response
from app.context import AppContext
from app.models import BankAccount, Company, Prefecture, User


@pytest.fixture
def base_company_data():
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        prefecture_account = BankAccount(id=20000)
        prefecture = Prefecture(name="MyPrefecture", bank_account_id=prefecture_account.id)
        session.add(prefecture)

        founder_account = BankAccount(id=50000)
        founder = User(
            bank_account_id=founder_account.id,
            prefecture_id=None,
            name="Test",
            last_name="User",
            patronymic="X",
            login="founder1",
            password="pass",
            sex="male",
            bonus=0,
            birthday=datetime.now(),
            is_admin=False,
        )
        ceo_account = BankAccount(id=60000)
        ceo = User(
            bank_account_id=ceo_account.id,
            prefecture_id=None,
            name="CEO",
            last_name="Leader",
            patronymic="Y",
            login="ceo1",
            password="pass",
            sex="male",
            bonus=0,
            birthday=datetime.now(),
            is_admin=False,
        )

        session.add_all([founder_account, founder, ceo_account, ceo, prefecture_account, prefecture])
        session.commit()

        yield {"prefecture": prefecture, "founder": founder, "ceo": ceo}

        session.execute(orm.delete(Company))
        session.execute(orm.delete(Prefecture))
        session.execute(orm.delete(User))
        session.execute(orm.delete(BankAccount))
        session.commit()


def test_create_company_with_ceo_ok(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]
    ceo = base_company_data["ceo"]

    req = Request(
        create_company=CreateCompanyRequest(
            name="CorpWithCEO",
            about="CEO inside",
            prefecture="MyPrefecture",
            founders=[Founder(bank_account_id=founder.bank_account_id, share=0.5)],
            ceo_bank_account_id=ceo.bank_account_id
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.OK


def test_create_company_missing_ceo_record(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]

    req = Request(
        create_company=CreateCompanyRequest(
            name="CorpMissingCEO",
            about="Oops",
            prefecture="MyPrefecture",
            founders=[Founder(bank_account_id=founder.bank_account_id, share=0.5)],
            ceo_bank_account_id=999999
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.MISSING_FOUNDERS
