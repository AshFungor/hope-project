import pytest
import sqlalchemy as orm
import datetime

from app.codegen.hope import Request, Response
from app.codegen.company import AllCompaniesRequest, AllCompaniesResponse
from app.codegen.company import GetCompanyRequest, GetCompanyResponse
from app.context import AppContext
from app.models import Company, User, User2Company, BankAccount, Prefecture, Role, Sex


@pytest.fixture
def company_data():
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session

        user_bank_account = BankAccount(id=5000)
        company_bank_account = BankAccount(id=6000)

        prefecture = Prefecture(name="Pref", bank_account_id=7000)

        user = User(
            bank_account_id=user_bank_account.id,
            prefecture_id=None,
            name="name",
            last_name="name",
            patronymic="name",
            login="name",
            password="1234",
            sex=Sex.MALE,
            bonus=0,
            birthday=datetime.date(1990, 1, 1)
        )

        company = Company(
            bank_account_id=company_bank_account.id,
            prefecture_id=1,
            name="TestCompany",
            about="A company for testing"
        )

        link = User2Company(
            user_id=None,
            company_id=None,
            role=Role.CEO,
            ratio=100,
            employed_at=datetime.datetime.now()
        )

        session.add_all([user_bank_account, company_bank_account, prefecture, user, company])
        session.flush()

        link.user_id = user.id
        link.company_id = company.id

        session.add(link)
        session.commit()

        yield {
            "user": user,
            "company": company
        }

        session.execute(orm.delete(User2Company))
        session.execute(orm.delete(Company))
        session.execute(orm.delete(User))
        session.execute(orm.delete(BankAccount))
        session.execute(orm.delete(Prefecture))
        session.commit()


def test_get_all_companies_related(client, company_data, logged_in_admin):
    req = Request(all_companies=AllCompaniesRequest(
        related_user_bank_account_id=company_data["user"].bank_account_id
    ))
    resp = client.post("/api/companies/all", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    names = [c.name for c in r.all_companies.companies]
    assert "TestCompany" in names


def test_get_all_companies_global(client, company_data, logged_in_admin):
    req = Request(all_companies=AllCompaniesRequest(globally=True))
    resp = client.post("/api/companies/all", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    names = [c.name for c in r.all_companies.companies]
    assert "TestCompany" in names


def test_get_all_companies_invalid_user(client, company_data, logged_in_admin):
    req = Request(all_companies=AllCompaniesRequest(related_user_bank_account_id=999999))
    resp = client.post("/api/companies/all", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert len(r.all_companies.companies) == 0


def test_get_company(client, company_data, logged_in_admin):
    req = Request(get_company=GetCompanyRequest(
        company_bank_account_id=company_data["company"].bank_account_id
    ))
    resp = client.post("/api/company/get", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.get_company.company.name == company_data["company"].name
