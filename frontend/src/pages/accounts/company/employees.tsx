import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import { Hope } from '@app/api/api';
import { useUser } from '@app/contexts/user';

import { Request } from '@app/codegen/app/protos/request';
import { AllEmployeesRequest, AllEmployeesResponse } from '@app/codegen/app/protos/company/employees';
import { FireRequest, FireResponse, FireResponse_Status } from '@app/codegen/app/protos/company/fire';
import { EmployeeRole } from '@app/codegen/app/protos/types/company';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

interface CompanyEmployeesProps {
    employees: AllEmployeesResponse['employees'];
    canFireKeyRoles: boolean;
    canFireWorkers: boolean;
    onFire: (bankAccountId: number, role: EmployeeRole) => void;
}

const roleLabel = (role: EmployeeRole) => {
    switch (role) {
        case EmployeeRole.CEO: return 'Генеральный директор';
        case EmployeeRole.CFO: return 'Финансовый директор';
        case EmployeeRole.MARKETING_MANAGER: return 'Маркетолог';
        case EmployeeRole.PRODUCTION_MANAGER: return 'Производственный директор';
        case EmployeeRole.EMPLOYEE: return 'Сотрудник';
        default: return 'Роль неизвестна';
    }
};

export function CompanyEmployees({
    employees,
    canFireKeyRoles,
    canFireWorkers,
    onFire,
}: CompanyEmployeesProps) {
    return (
        <Box sx={{ mt: 4 }}>
            <Typography variant="h6" sx={{ mb: 3 }}>
                Сотрудники
            </Typography>

            <Box sx={{ overflowX: 'auto' }}>
                <Table sx={{ minWidth: 600 }}>
                    <TableHead>
                        <TableRow>
                            <TableCell>Имя</TableCell>
                            <TableCell>Фамилия</TableCell>
                            <TableCell>Отчество</TableCell>
                            <TableCell>Должность</TableCell>
                            {(canFireKeyRoles || canFireWorkers) && <TableCell />}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {employees.map((e, index) => {
                            const canFire =
                                (canFireKeyRoles && e.role !== EmployeeRole.EMPLOYEE && e.role !== EmployeeRole.CEO) ||
                                (canFireWorkers && e.role === EmployeeRole.EMPLOYEE);

                            return (
                                <TableRow key={index}>
                                    <TableCell>{e.info?.name}</TableCell>
                                    <TableCell>{e.info?.lastName}</TableCell>
                                    <TableCell>{e.info?.patronymic}</TableCell>
                                    <TableCell>{roleLabel(e.role)}</TableCell>
                                    {(canFireKeyRoles || canFireWorkers) && (
                                        <TableCell>
                                            {canFire ? (
                                                <Button
                                                    variant="outlined"
                                                    size="small"
                                                    color="error"
                                                    onClick={() => onFire(e.info?.bankAccountId ?? 0, e.role)}
                                                >
                                                    Уволить
                                                </Button>
                                            ) : (
                                                <Typography variant="body2" color="text.secondary">-</Typography>
                                            )}
                                        </TableCell>
                                    )}
                                </TableRow>
                            );
                        })}
                    </TableBody>
                </Table>
            </Box>
        </Box>
    );
}


export default function CompanyEmployeesPage() {
    const { companyId } = useParams<{ companyId: string }>();
    const { currentUser } = useUser();

    const [employees, setEmployees] = useState<AllEmployeesResponse['employees']>([]);
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
                setMessage('Сотрудник уволен.');
                setStatus(AlertStatus.Info);
                await fetchEmployees();
                break;
            case FireResponse_Status.USER_NOT_FOUND:
                setMessage('Пользователь не найден.');
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.COMPANY_NOT_FOUND:
                setMessage('Фирма не найдена.');
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.EMPLOYER_NOT_AUTHORIZED:
                setMessage('У вас нет прав для увольнения этого сотрудника.');
                setStatus(AlertStatus.Error);
                break;
            case FireResponse_Status.EMPLOYEE_IS_NOT_SUITABLE:
                setMessage('Нельзя уволить этого сотрудника.');
                setStatus(AlertStatus.Error);
                break;
            default:
                setMessage('Неизвестная ошибка при увольнении.');
                setStatus(AlertStatus.Error);
        }
    };

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" sx={{ mb: 4 }} align="center">
                <strong>Список сотрудников</strong>
            </Typography>
            <MessageAlert message={message} status={status} />
            <CompanyEmployees
                employees={employees}
                canFireKeyRoles={canFireKeyRoles}
                canFireWorkers={canFireWorkers}
                onFire={handleFire}
            />
        </Container>
    );
}
