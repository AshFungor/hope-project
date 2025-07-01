import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useUser } from "@app/contexts/user";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";

import { GetCompanyRequest, GetCompanyResponse } from "@app/codegen/app/protos/company/get";
import { CurrentPrefectureRequest, CurrentPrefectureResponse } from "@app/codegen/app/protos/prefecture/current";
import { GetLastGoalRequest, GetLastGoalResponse } from "@app/codegen/app/protos/goal/last";
import { AllEmployeesRequest, AllEmployeesResponse } from "@app/codegen/app/protos/company/employees";
import { ProductCountsRequest, ProductCountsResponse } from "@app/codegen/app/protos/product/count";

import { Goal as GoalModel } from "@app/api/sub/goal";
import { EmployeeRole } from "@app/codegen/app/protos/types/company";

import BalanceSection from "@app/widgets/shared/balance";
import GoalSection from "@app/widgets/shared/goal";

interface Company {
    bankAccountId: number;
    name: string;
    about: string;
}

interface CEO {
    name: string;
    lastName: string;
    patronymic: string;
}

export default function CompanyCabinetPage() {
    const { companyId } = useParams<{ companyId: string }>();
    const { currentUser } = useUser();
    const navigate = useNavigate();

    const [goal, setGoal] = useState<GoalModel | null>(null);
    const [balance, setBalance] = useState(0);
    const [company, setCompany] = useState<Company | null>(null);
    const [ceo, setCeo] = useState<CEO | null>(null);
    const [prefectureName, setPrefectureName] = useState<string>("");

    const [fCeo, setFCeo] = useState(false);
    const [fCfo, setFCfo] = useState(false);
    const [fMark, setFMark] = useState(false);
    const [fProd, setFProd] = useState(false);

    useEffect(() => {
        const loadCompanyData = async () => {
            if (!companyId) return;

            const companyReq: GetCompanyRequest = {
                companyBankAccountId: Number(companyId),
            };
            const companyResp = await Hope.send(Request.create({ getCompany: companyReq })) as {
                getCompany?: GetCompanyResponse;
            };

            const c = companyResp.getCompany?.company;
            if (!c) return;

            setCompany({
                bankAccountId: Number(c.bankAccountId),
                name: c.name,
                about: c.about,
            });

            const employeesReq: AllEmployeesRequest = {
                companyBankAccountId: c.bankAccountId,
            };
            const employeesResp = await Hope.send(Request.create({ allEmployees: employeesReq })) as {
                allEmployees?: AllEmployeesResponse;
            };

            const employees = employeesResp.allEmployees?.employees ?? [];

            employees.forEach((e) => {
                if (e.role === EmployeeRole.CEO) {
                    setCeo({
                        name: e.info?.name ?? "",
                        lastName: e.info?.lastName ?? "",
                        patronymic: e.info?.patronymic ?? "",
                    })
                }

                if (e.info?.bankAccountId != currentUser?.bankAccountId) {
                    return;
                }

                if (e.role === EmployeeRole.CEO) setFCeo(true);
                if (e.role === EmployeeRole.CFO) setFCfo(true);
                if (e.role === EmployeeRole.MARKETING_MANAGER) setFMark(true);
                if (e.role === EmployeeRole.PRODUCTION_MANAGER) setFProd(true);
            });

            const prefReq: CurrentPrefectureRequest = { bankAccountId: c.bankAccountId };
            const prefResp = await Hope.send(Request.create({ currentPrefecture: prefReq })) as {
                currentPrefecture?: CurrentPrefectureResponse;
            };
            setPrefectureName(prefResp.currentPrefecture?.prefecture?.name ?? "");

            const goalReq: GetLastGoalRequest = { bankAccountId: Number(companyId) };
            const goalResp = await Hope.send(Request.create({ lastGoal: goalReq })) as {
                lastGoal?: GetLastGoalResponse;
            };

            const g = goalResp.lastGoal?.goal;
            if (g) {
                setGoal(new GoalModel(Number(g.bankAccountId), Number(g.value)));
            } else {
                if (fCeo) {
                    navigate(`/company/${companyId}/goal/new`);
                    return;
                }
                setGoal(null);
            }

            const countReq: ProductCountsRequest = {
                bankAccountId: Number(companyId),
            };
            const countResp = await Hope.send(Request.create({ productCounts: countReq })) as {
                productCounts?: ProductCountsResponse;
            };
            const counts = countResp?.productCounts?.products ?? [];
            const money = counts.find(p => p.product?.category === "MONEY");
            setBalance(money?.count ?? 0);
        };

        loadCompanyData();
    }, [companyId, navigate, fCeo]);

    const handleNavigate = (path: string) => {
        navigate(path);
    };

    return (
        <div className="container mt-4">
            {company && (
                <>
                    <div className="text-wrap text-center d-flex flex-wrap align-items-center justify-content-center mb-3">
                        <h3><strong>Фирма "{company.name}"</strong></h3>
                    </div>

                    <GoalSection goal={goal} balance={balance} />
                    <BalanceSection current={balance} />

                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <td colSpan={2}>Данные о фирме:</td>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>Номер банковского счета:</th>
                                <td>{company.bankAccountId}</td>
                            </tr>
                            <tr>
                                <th>Описание фирмы:</th>
                                <td>{company.about}</td>
                            </tr>
                            <tr>
                                <th>Ген. директор:</th>
                                <td>{ceo?.name} {ceo?.patronymic} {ceo?.lastName}</td>
                            </tr>
                            <tr>
                                <th>Префектура:</th>
                                <td>{prefectureName}</td>
                            </tr>
                        </tbody>
                    </table>

                    <div className="d-grid gap-2 mb-5">
                        {fCfo && (
                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/money`)}
                            >
                                Перевод средств
                            </button>
                        )}

                        {fMark && (
                            <>
                                <button
                                    className="btn btn-outline-dark btn-lg mb-3"
                                    onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/product`)}
                                >
                                    Выставить счёт
                                </button>
                                <button
                                    className="btn btn-outline-dark btn-lg mb-3"
                                    onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/unpaid`)}
                                >
                                    Входящие счета
                                </button>
                            </>
                        )}

                        {fProd && (
                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/history`)}
                            >
                                История счетов
                            </button>
                        )}
                    </div>

                    {fProd && (
                        <div className="d-grid gap-2 mb-5">
                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/products`)}
                            >
                                Наши ресурсы/энергия/товары
                            </button>

                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/production/employ`)}
                            >
                                Принять на работу
                            </button>
                        </div>
                    )}

                    {fCeo && (
                        <div className="d-grid gap-2 mb-5">
                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/workers`)}
                            >
                                Сотрудники
                            </button>

                            <button
                                className="btn btn-outline-dark btn-lg mb-3"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/ceo/employ`)}
                            >
                                Принять на работу
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
