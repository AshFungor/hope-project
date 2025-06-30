import pytest
import sqlalchemy as orm

from datetime import datetime

from app.context import AppContext
from app.models import User, BankAccount, Prefecture, Company
from app.codegen.hope import Request, Response
from app.codegen.company import CreateCompanyRequest, Founder, CreateCompanyResponseStatus


@pytest.fixture
def base_company_data():
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        prefecture_account = BankAccount(id=20000)
        prefecture = Prefecture(name="MyPrefecture", bank_account_id=prefecture_account.id)
        session.add(prefecture)

        account = BankAccount(id=50000)
        user = User(
            bank_account_id=account.id,
            prefecture_id=None,
            name="Test",
            last_name="User",
            patronymic="X",
            login="founder1",
            password="pass",
            sex="male",
            bonus=0,
            birthday=datetime.now(),
            is_admin=False
        )
        session.add_all([account, user, prefecture_account, prefecture])
        session.commit()

        yield {
            "prefecture": prefecture,
            "founder": user
        }

        session.execute(orm.delete(Company))
        session.execute(orm.delete(Prefecture))
        session.execute(orm.delete(User))
        session.execute(orm.delete(BankAccount))
        session.commit()


def test_create_company_ok(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]
    req = Request(
        create_company=CreateCompanyRequest(
            name="NewCorp",
            about="About us",
            prefecture="MyPrefecture",
            founders=[
                Founder(account_id=founder.bank_account_id, share=0.5)
            ]
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.OK


def test_create_company_duplicate_name(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]

    req_ok = Request(
        create_company=CreateCompanyRequest(
            name="NewCorp",
            about="First attempt",
            prefecture="MyPrefecture",
            founders=[
                Founder(account_id=founder.bank_account_id, share=0.5)
            ]
        )
    )
    resp_ok = client.post("/api/company/create", data=bytes(req_ok))
    assert resp_ok.status_code == 200

    r_ok = Response().parse(resp_ok.data)
    assert r_ok.create_company.status == CreateCompanyResponseStatus.OK

    req_dup = Request(
        create_company=CreateCompanyRequest(
            name="NewCorp",  # Та же компания
            about="Second attempt",
            prefecture="MyPrefecture",
            founders=[
                Founder(account_id=founder.bank_account_id, share=0.5)
            ]
        )
    )
    resp_dup = client.post("/api/company/create", data=bytes(req_dup))
    assert resp_dup.status_code == 200

    r_dup = Response().parse(resp_dup.data)
    assert r_dup.create_company.status == CreateCompanyResponseStatus.DUPLICATE_NAME


def test_create_company_missing_prefecture(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]

    req = Request(
        create_company=CreateCompanyRequest(
            name="NoPref",
            about="Oops",
            prefecture="UnknownPrefecture",
            founders=[
                Founder(account_id=founder.bank_account_id, share=0.5)
            ]
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.MISSING_PREFECTURE


def test_create_company_no_founders(client, logged_in_admin, base_company_data):
    req = Request(
        create_company=CreateCompanyRequest(
            name="EmptyFounders",
            about="Oops",
            prefecture="MyPrefecture",
            founders=[]
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.MISSING_FOUNDERS


def test_create_company_duplicate_founders(client, logged_in_admin, base_company_data):
    founder = base_company_data["founder"]

    req = Request(
        create_company=CreateCompanyRequest(
            name="DuplicateFounderCorp",
            about="Oops",
            prefecture="MyPrefecture",
            founders=[
                Founder(account_id=founder.bank_account_id, share=0.5),
                Founder(account_id=founder.bank_account_id, share=0.5)
            ]
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.DUPLICATE_FOUNDERS


def test_create_company_missing_founder_record(client, logged_in_admin, base_company_data):
    req = Request(
        create_company=CreateCompanyRequest(
            name="NoRecordCorp",
            about="Oops",
            prefecture="MyPrefecture",
            founders=[
                Founder(account_id=999999, share=0.5)  # Не существует
            ]
        )
    )
    resp = client.post("/api/company/create", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.create_company.status == CreateCompanyResponseStatus.MISSING_FOUNDERS
