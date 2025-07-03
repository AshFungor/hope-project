import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import {
	EmployRequest,
	EmployResponse,
	EmployResponse_Status,
} from '@app/codegen/app/protos/company/employ';
import { EmployeeRole } from '@app/codegen/app/protos/types/company';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';

interface CompanyEmployPageProps {
	permittedRoles: EmployeeRole[];
}

export default function CompanyEmployPage({ permittedRoles }: CompanyEmployPageProps) {
	const { companyId } = useParams<{ companyId: string }>();
	const navigate = useNavigate();

	const [accountId, setAccountId] = useState('');
	const [role, setRole] = useState<EmployeeRole>(permittedRoles[0] ?? EmployeeRole.EMPLOYEE);
	const [message, setMessage] = useState<string | null>(null);
	const [status, setStatus] = useState<AlertStatus>(AlertStatus.Info);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!accountId || !companyId) {
			setMessage('Заполните все поля.');
			setStatus(AlertStatus.Error);
			return;
		}

		const req: EmployRequest = {
			newEmployeeBankAccountId: Number(accountId),
			companyBankAccountId: Number(companyId),
			role: role,
		};

		const response = (await Hope.send(Request.create({ employ: req }))) as {
			employ?: EmployResponse;
		};

		switch (response.employ?.status) {
			case EmployResponse_Status.OK:
				setMessage('Сотрудник успешно принят на работу!');
				setStatus(AlertStatus.Info);
				break;
			case EmployResponse_Status.HAS_ROLE_ALREADY:
				setMessage('У пользователя уже есть критическая роль');
				setStatus(AlertStatus.Error);
				break;
			case EmployResponse_Status.USER_NOT_FOUND:
				setMessage('Пользователь не найден');
				setStatus(AlertStatus.Error);
				break;
			case EmployResponse_Status.COMPANY_NOT_FOUND:
				setMessage('Фирма не найдена');
				setStatus(AlertStatus.Error);
				break;
			case EmployResponse_Status.EMPLOYEE_IS_NOT_SUITABLE:
				setMessage('Работадать не может нанять данного сотрудника');
				setStatus(AlertStatus.Error);
				break;
			case EmployResponse_Status.EMPLOYER_NOT_AUTHORIZED:
				setMessage('Текущий сотрудник не может нанимать других сотрудников');
				setStatus(AlertStatus.Error);
				break;
			default:
				setMessage('Неизвестная ошибка.');
				setStatus(AlertStatus.Error);
		}
	};

	return (
		<Box sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
			<Box sx={{ textAlign: 'center', mb: 4 }}>
				<Typography variant="h5">Приём на работу сотрудника</Typography>
				<Typography variant="body1">
					Номер фирмы: <strong>{companyId}</strong>
				</Typography>
			</Box>

			<MessageAlert message={message} status={status} />

			<Box component="form" onSubmit={handleSubmit}>
				<TextField
					label="Номер счёта нового сотрудника"
					type="number"
					value={accountId}
					onChange={(e) => setAccountId(e.target.value)}
					placeholder="Введите ID счёта"
					fullWidth
					sx={{ mb: 3 }}
				/>

				<FormControl fullWidth sx={{ mb: 3 }}>
					<InputLabel id="role-label">Роль</InputLabel>
					<Select
						labelId="role-label"
						value={role}
						label="Роль"
						onChange={(e) => setRole(Number(e.target.value))}
					>
						{permittedRoles.map((r) => (
							<MenuItem key={r} value={r}>
								{roleLabel(r)}
							</MenuItem>
						))}
					</Select>
				</FormControl>

				<Stack spacing={2}>
					<Button variant="contained" color="success" type="submit">
						Принять на работу
					</Button>
					<Button variant="outlined" onClick={() => navigate(-1)}>
						Назад
					</Button>
				</Stack>
			</Box>
		</Box>
	);
}

function roleLabel(role: EmployeeRole): string {
	switch (role) {
		case EmployeeRole.EMPLOYEE:
			return 'Обычный сотрудник';
		case EmployeeRole.CFO:
			return 'Финансовый директор';
		case EmployeeRole.MARKETING_MANAGER:
			return 'Маркетолог';
		case EmployeeRole.PRODUCTION_MANAGER:
			return 'Производственный директор';
		case EmployeeRole.CEO:
			return 'Генеральный директор';
		default:
			return 'Неизвестная роль';
	}
}
