import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { useUser } from "@app/contexts/user";

import { Request } from "@app/codegen/app/protos/request";
import { AllEmployeesRequest, AllEmployeesResponse } from "@app/codegen/app/protos/company/employees";
import { FireRequest, FireResponse, FireResponse_Status } from "@app/codegen/app/protos/company/fire";
import { EmployeeRole } from "@app/codegen/app/protos/types/company";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

interface CompanyEmployeesProps {
    employees: AllEmployeesResponse["employees"];
    canFireKeyRoles: boolean;
    canFireWorkers: boolean;
    onFire: (bankAccountId: number, role: EmployeeRole) => void;
}

const roleLabel = (role: EmployeeRole) => {
    switch (role) {
        case EmployeeRole.CEO: return "Генеральный директор";
        case EmployeeRole.CFO: return "Финансовый директор";
        case EmployeeRole.MARKETING_MANAGER: return "Маркетолог";
        case EmployeeRole.PRODUCTION_MANAGER: return "Производственный директор";
        case EmployeeRole.EMPLOYEE: return "Сотрудник";
        default: return "Роль неизвестна";
    }
};

export function CompanyEmployees({
    employees,
    canFireKeyRoles,
    canFireWorkers,
    onFire
}: CompanyEmployeesProps) {
    return (
        <div className="mt-4">
            <h5 className="mb-3">Сотрудники</h5>
            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>Имя</th>
                        <th>Фамилия</th>
                        <th>Отчество</th>
                        <th>Должность</th>
                        {(canFireKeyRoles || canFireWorkers) && <th></th>}
                    </tr>
                </thead>
                <tbody>
                    {employees.map((e, index) => {
                        const canFire =
                            (canFireKeyRoles && e.role !== EmployeeRole.EMPLOYEE) ||
                            (canFireWorkers && e.role === EmployeeRole.EMPLOYEE);

                        return (
                            <tr key={index}>
                                <td>{e.info?.name}</td>
                                <td>{e.info?.lastName}</td>
                                <td>{e.info?.patronymic}</td>
                                <td>{roleLabel(e.role)}</td>
                                {(canFireKeyRoles || canFireWorkers) && (
                                    <td>
                                        {canFire ? (
                                            <button
                                                className="btn btn-sm btn-outline-danger"
                                                onClick={() => onFire(e.info?.bankAccountId ?? 0, e.role)}
                                            >
                                                Уволить
                                            </button>
                                        ) : (
                                            <span className="text-muted">-</span>
                                        )}
                                    </td>
                                )}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

export default function CompanyEmployeesPage() {
    const { companyId } = useParams<{ companyId: string }>();
    const { currentUser } = useUser();

    const [employees, setEmployees] = useState<AllEmployeesResponse["employees"]>([]);
    const [canFireKeyRoles, setCanFireKeyRoles] = useState(false);
    const [canFireWorkers, setCanFireWorkers] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [status, setStatus] = useState<AlertStatus>(AlertStatus.Info);

    const fetchEmployees = async () => {
        if (!companyId) return;

        const req: AllEmployeesRequest = {
            companyBankAccountId: Number(companyId),
        };

        const response = await Hope.send(
            Request.create({ allEmployees: req })
        ) as { allEmployees?: AllEmployeesResponse };

        const list = response.allEmployees?.employees ?? [];
        setEmployees(list);

        const me = list.find(e => e.info?.bankAccountId === currentUser?.bankAccountId);

        if (me) {
            if (me.role === EmployeeRole.CEO) {
                setCanFireKeyRoles(true);
            }
            if (me.role === EmployeeRole.PRODUCTION_MANAGER) {
                setCanFireWorkers(true);
            }
        }
    };

    useEffect(() => {
        fetchEmployees();
    }, [companyId, currentUser]);

    const handleFire = async (accountId: number) => {
        if (!companyId) return;

        const fireReq: FireRequest = {
            employeeBankAccountId: accountId,
            companyBankAccountId: Number(companyId),
        };

        const response = await Hope.send(
            Request.create({ fire: fireReq })
        ) as { fire?: FireResponse };

        switch (response.fire?.status) {
            case FireResponse_Status.OK:
                setMessage("Сотрудник уволен.");
                setStatus(AlertStatus.Info);
                await fetchEmployees();
                break;
            case FireResponse_Status.USER_NOT_FOUND:
                setMessage("Пользователь не найден.");
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.COMPANY_NOT_FOUND:
                setMessage("Фирма не найдена.");
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.EMPLOYER_NOT_AUTHORIZED:
                setMessage("У вас нет прав для увольнения этого сотрудника.");
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.EMPLOYEE_IS_NOT_SUITABLE:
                setMessage("Нельзя уволить этого сотрудника.");
                setStatus(AlertStatus.Error);
                break;
            default:
                setMessage("Неизвестная ошибка при увольнении.");
                setStatus(AlertStatus.Error);
        }
    };

    return (
        <div className="container mt-4">
            <h3 className="mb-4 text-center"><strong>Список сотрудников</strong></h3>
            <MessageAlert message={message} status={status} />
            <CompanyEmployees
                employees={employees}
                canFireKeyRoles={canFireKeyRoles}
                canFireWorkers={canFireWorkers}
                onFire={handleFire}
            />
        </div>
    );
}
