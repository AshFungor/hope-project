import pytest
import sqlalchemy as orm

from datetime import date, datetime
from dataclasses import dataclass

from app.context import AppContext
from app.models import BankAccount, User, Company, User2Company, Role, Sex

from app.codegen.hope import Request, Response
from app.codegen.company import EmployResponseStatus, EmployRequest
from app.codegen.types import EmployeeRole


@dataclass
class EmployData:
    employee_account: int
    company_account: int


@pytest.fixture
def employ_data(logged_in_normal):
    ctx = AppContext.safe_load()
    normal_user_id: int = logged_in_normal

    with ctx.app.app_context():
        session = ctx.database.session

        data = EmployData(
            employee_account=50000,
            company_account=40000
        )
        employee_bank_account = BankAccount(id=data.employee_account)
        company_bank_account = BankAccount(id=data.company_account)

        new_employee = User(
            bank_account_id=employee_bank_account.id,
            prefecture_id=None,
            name="",
            last_name="",
            patronymic="",
            login="",
            password="",
            sex=Sex.MALE,
            bonus=0,
            birthday=date(1995, 1, 1)
        )

        company = Company(
            bank_account_id=company_bank_account.id,
            prefecture_id=1,
            name="",
            about=""
        )

        session.add_all([employee_bank_account, company_bank_account, new_employee, company])
        session.flush()

        ceo_link = User2Company(
            user_id=normal_user_id, # provided by outer context
            company_id=company.id,
            role=Role.CEO,
            ratio=0,
            employed_at=datetime.now()
        )

        session.add(ceo_link)
        session.commit()

        yield {
            "employee": new_employee,
            "company": company,
        }

        session.execute(orm.delete(User2Company))
        session.execute(orm.delete(Company))
        session.execute(orm.delete(User))
        session.execute(orm.delete(BankAccount))
        session.commit()


def test_employ_ok_ceo(client, employ_data, logged_in_normal):
    employee = employ_data["employee"]
    company = employ_data["company"]

    req = Request(employ=EmployRequest(
        new_employee_bank_account_id=employee.bank_account_id,
        company_bank_account_id=company.bank_account_id,
        role=EmployeeRole.CFO
    ))
    resp = client.post("/api/company/employ", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.employ.status == EmployResponseStatus.OK


def test_employ_already_has_critical(client, employ_data, logged_in_normal):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session
        link = User2Company(
            user_id=employ_data["employee"].id,
            company_id=employ_data["company"].id,
            role=Role.PRODUCTION_MANAGER,
            ratio=0,
            employed_at=datetime.now()
        )
        session.add(link)
        session.commit()

    req = Request(employ=EmployRequest(
        new_employee_bank_account_id=employ_data["employee"].bank_account_id,
        company_bank_account_id=employ_data["company"].bank_account_id,
        role=EmployeeRole.CFO
    ))
    resp = client.post("/api/company/employ", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.employ.status == EmployResponseStatus.HAS_ROLE_ALREADY


def test_employ_worker_by_production_manager(client, employ_data, logged_in_normal):
    ctx = AppContext.safe_load()
    with ctx.app.app_context():
        session = ctx.database.session
        link = session.scalar(
            orm.select(User2Company).filter(User2Company.user_id == 1)
        )
        link.role = Role.PRODUCTION_MANAGER
        session.commit()

    req_ok = Request(employ=EmployRequest(
        new_employee_bank_account_id=employ_data["employee"].bank_account_id,
        company_bank_account_id=employ_data["company"].bank_account_id,
        role=EmployeeRole.EMPLOYEE
    ))
    resp_ok = client.post("/api/company/employ", data=bytes(req_ok))
    assert resp_ok.status_code == 200
    r = Response().parse(resp_ok.data)
    assert r.employ.status == EmployResponseStatus.OK

    req_fail = Request(employ=EmployRequest(
        new_employee_bank_account_id=employ_data["employee"].bank_account_id,
        company_bank_account_id=employ_data["company"].bank_account_id,
        role=EmployeeRole.CFO
    ))
    resp_fail = client.post("/api/company/employ", data=bytes(req_fail))
    assert resp_fail.status_code == 200
    r = Response().parse(resp_fail.data)
    assert r.employ.status == EmployResponseStatus.HAS_ROLE_ALREADY


def test_employ_user_not_found(client, employ_data, logged_in_admin):
    req = Request(employ=EmployRequest(
        new_employee_bank_account_id=999999,
        company_bank_account_id=employ_data["company"].bank_account_id,
        role=EmployeeRole.PRODUCTION_MANAGER
    ))
    resp = client.post("/api/company/employ", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.employ.status == EmployResponseStatus.USER_NOT_FOUND


def test_employ_company_not_found(client, employ_data, logged_in_normal):
    req = Request(employ=EmployRequest(
        new_employee_bank_account_id=employ_data["employee"].bank_account_id,
        company_bank_account_id=999999,
        role=EmployeeRole.EMPLOYEE
    ))
    resp = client.post("/api/company/employ", data=bytes(req))
    assert resp.status_code == 200

    r = Response().parse(resp.data)
    assert r.employ.status == EmployResponseStatus.COMPANY_NOT_FOUND
