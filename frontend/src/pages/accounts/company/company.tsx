import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';

import { GetCompanyRequest, GetCompanyResponse } from '@app/codegen/app/protos/company/get';
import { CurrentPrefectureRequest, CurrentPrefectureResponse } from '@app/codegen/app/protos/prefecture/current';
import { GetLastGoalRequest, GetLastGoalResponse } from '@app/codegen/app/protos/goal/last';
import { AllEmployeesRequest, AllEmployeesResponse } from '@app/codegen/app/protos/company/employees';
import { ProductCountsRequest, ProductCountsResponse } from '@app/codegen/app/protos/product/count';

import { Goal as GoalModel } from '@app/api/sub/goal';
import { EmployeeRole } from '@app/codegen/app/protos/types/company';

import BalanceSection from '@app/widgets/shared/balance';
import GoalSection from '@app/widgets/shared/goal';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';

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
    const [prefectureName, setPrefectureName] = useState<string>('');

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
                        name: e.info?.name ?? '',
                        lastName: e.info?.lastName ?? '',
                        patronymic: e.info?.patronymic ?? '',
                    });
                }

                if (e.info?.bankAccountId !== currentUser?.bankAccountId) {
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
            setPrefectureName(prefResp.currentPrefecture?.prefecture?.name ?? '');

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
            
            const grpcRequest = Request.create({ productCounts: countReq });
            const countResp = await Hope.send(grpcRequest) as {
                productCounts?: ProductCountsResponse;
            };
            
            const counts = countResp?.productCounts?.products ?? [];
            const money = counts.find(p => p.product?.category === 'MONEY');
            
            setBalance(money?.count ?? 0);
        };

        loadCompanyData();
    }, [companyId, navigate, fCeo]);

    const handleNavigate = (path: string) => {
        navigate(path);
    };

    return (
        <Container sx={{ mt: 4 }}>
            {company && (
                <>
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                        <Typography variant="h4" component="h3">
                            Фирма "{company.name}"
                        </Typography>
                    </Box>

                    <GoalSection goal={goal} balance={balance} />
                    <BalanceSection current={balance} />

                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell colSpan={2}>Данные о фирме:</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            <TableRow>
                                <TableCell>Номер банковского счета:</TableCell>
                                <TableCell>{company.bankAccountId}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Описание фирмы:</TableCell>
                                <TableCell>{company.about}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Ген. директор:</TableCell>
                                <TableCell>{ceo?.name} {ceo?.patronymic} {ceo?.lastName}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Префектура:</TableCell>
                                <TableCell>{prefectureName}</TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>

                    <Stack spacing={2} sx={{ my: 5 }}>
                        {fCfo && (
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/money`)}
                            >
                                Перевод средств
                            </Button>
                        )}

                        {fMark && (
                            <>
                                <Button
                                    variant="outlined"
                                    size="large"
                                    onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/product`)}
                                >
                                    Выставить счёт
                                </Button>
                                <Button
                                    variant="outlined"
                                    size="large"
                                    onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/unpaid`)}
                                >
                                    Входящие счета
                                </Button>
                            </>
                        )}

                        {fProd && (
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/proposal/history`)}
                            >
                                История счетов
                            </Button>
                        )}
                    </Stack>

                    {fProd && (
                        <Stack spacing={2} sx={{ mb: 5 }}>
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/products`)}
                            >
                                Наши ресурсы/энергия/товары
                            </Button>

                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/production/employ`)}
                            >
                                Принять на работу
                            </Button>
                        </Stack>
                    )}

                    {fCeo && (
                        <Stack spacing={2} sx={{ mb: 5 }}>
                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/workers`)}
                            >
                                Сотрудники
                            </Button>

                            <Button
                                variant="outlined"
                                size="large"
                                onClick={() => handleNavigate(`/company/${company.bankAccountId}/ceo/employ`)}
                            >
                                Принять на работу
                            </Button>
                        </Stack>
                    )}
                </>
            )}
        </Container>
    );
}
