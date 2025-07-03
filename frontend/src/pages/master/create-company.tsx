import React, { useState, useEffect } from 'react';

import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import {
	CreateCompanyRequest,
	CreateCompanyResponse,
	CreateCompanyResponse_Status,
	Founder,
} from '@app/codegen/app/protos/company/create';
import {
	AllPrefecturesRequest,
	AllPrefecturesResponse,
} from '@app/codegen/app/protos/prefecture/all';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

interface Prefecture {
	id: number;
	name: string;
}

export default function CreateCompanyPage() {
	const [companyName, setCompanyName] = useState('');
	const [about, setAbout] = useState('');
	const [prefectureId, setPrefectureId] = useState('');
	const [founders, setFounders] = useState<Founder[]>([]);
	const [ceoId, setCeoId] = useState<number>(0);
	const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
	const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

	useEffect(() => {
		const fetchPrefectures = async () => {
			try {
				const req = AllPrefecturesRequest.create({});
				const response = (await Hope.send(Request.create({ allPrefectures: req }))) as {
					allPrefectures?: AllPrefecturesResponse;
				};
				const received = response.allPrefectures?.prefectures ?? [];
				setPrefectures(
					received.map((p) => ({
						id: Number(p.bankAccountId),
						name: p.name,
					}))
				);
			} catch (err) {
				console.error('Failed to load prefectures:', err);
			}
		};
		fetchPrefectures();
	}, []);

	const addFounder = () => {
		setFounders([...founders, Founder.create({ bankAccountId: 0, share: 0 })]);
	};

	const updateFounder = (index: number, field: 'accountId' | 'share', value: number) => {
		const updated = [...founders];
		if (field === 'accountId') updated[index].bankAccountId = value;
		if (field === 'share') updated[index].share = value;
		setFounders(updated);
	};

	const removeFounder = (index: number) => {
		setFounders(founders.filter((_, i) => i !== index));
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (!companyName || !about || !prefectureId || founders.length === 0 || ceoId <= 0) {
			setMessage({
				contents: 'Все поля обязательны, включая генерального директора',
				status: AlertStatus.Error,
			});
			return;
		}

		const invalidFounder = founders.find(
			(f) =>
				!f.bankAccountId ||
				f.bankAccountId <= 0 ||
				!f.share ||
				f.share <= 0 ||
				f.share > 100
		);

		if (invalidFounder) {
			setMessage({
				contents: 'ID учредителя должен быть > 0, а доля — от 1% до 100%.',
				status: AlertStatus.Error,
			});
			return;
		}

		const request = CreateCompanyRequest.create({
			name: companyName,
			about: about,
			prefecture: prefectures.find((p) => p.id === parseInt(prefectureId))?.name ?? '',
			founders: founders.map((f) =>
				Founder.create({
					bankAccountId: f.bankAccountId,
					share: f.share / 100.0,
				})
			),
			ceoBankAccountId: ceoId,
		});

		const response = (await Hope.send(Request.create({ createCompany: request }))) as {
			createCompany?: CreateCompanyResponse;
		};

		switch (response.createCompany?.status) {
			case CreateCompanyResponse_Status.OK:
				setMessage({ contents: 'Фирма успешно создана!', status: AlertStatus.Info });
				setCompanyName('');
				setAbout('');
				setPrefectureId('');
				setFounders([]);
				setCeoId(0);
				break;
			case CreateCompanyResponse_Status.MISSING_FOUNDERS:
				setMessage({ contents: 'Не указаны учредители.', status: AlertStatus.Error });
				break;
			case CreateCompanyResponse_Status.DUPLICATE_FOUNDERS:
				setMessage({ contents: 'Учредители дублируются.', status: AlertStatus.Error });
				break;
			case CreateCompanyResponse_Status.MISSING_PREFECTURE:
				setMessage({ contents: 'Не выбрана префектура.', status: AlertStatus.Error });
				break;
			case CreateCompanyResponse_Status.DUPLICATE_NAME:
				setMessage({
					contents: 'Фирма с таким названием уже существует.',
					status: AlertStatus.Error,
				});
				break;
			default:
				setMessage({ contents: 'Неизвестная ошибка.', status: AlertStatus.Error });
		}
	};

	return (
		<Container sx={{ mt: 4 }}>
			<Typography variant="h4" align="center" sx={{ mb: 4 }}>
				Новая фирма
			</Typography>

			<Box
				component="form"
				onSubmit={handleSubmit}
				sx={{ display: 'flex', flexDirection: 'column', gap: 3, maxWidth: 600, mx: 'auto' }}
			>
				{message && <MessageAlert message={message.contents} status={message.status} />}

				<TextField
					label="Название фирмы"
					value={companyName}
					onChange={(e) => setCompanyName(e.target.value)}
					fullWidth
				/>

				<TextField
					label="Описание"
					value={about}
					onChange={(e) => setAbout(e.target.value)}
					fullWidth
				/>

				<Box>
					<Typography variant="subtitle1" sx={{ mb: 1 }}>
						Префектура
					</Typography>
					<Select
						value={prefectureId}
						onChange={(e) => setPrefectureId(e.target.value)}
						displayEmpty
						fullWidth
					>
						<MenuItem value="">
							<em>Выберите префектуру</em>
						</MenuItem>
						{prefectures.map((p) => (
							<MenuItem key={p.id} value={p.id}>
								{p.name}
							</MenuItem>
						))}
					</Select>
				</Box>

				<TextField
					label="ID Генерального директора (CEO)"
					type="number"
					value={ceoId === 0 ? '' : ceoId}
					onChange={(e) => setCeoId(Number(e.target.value))}
					placeholder="Введите ID счета CEO"
					fullWidth
				/>

				<Box>
					<Typography variant="subtitle1" sx={{ mb: 2 }}>
						Учредители
					</Typography>
					<Stack spacing={2}>
						{founders.map((founder, index) => (
							<Box key={index} sx={{ display: 'flex', gap: 2 }}>
								<TextField
									label="ID учредителя"
									type="number"
									value={founder.bankAccountId === 0 ? '' : founder.bankAccountId}
									onChange={(e) =>
										updateFounder(
											index,
											'accountId',
											parseInt(e.target.value.replace(/^0+/, '') || '0', 10)
										)
									}
									fullWidth
								/>
								<TextField
									label="Доля (%)"
									type="number"
									value={founder.share === 0 ? '' : founder.share}
									onChange={(e) =>
										updateFounder(
											index,
											'share',
											parseInt(e.target.value.replace(/^0+/, '') || '0', 10)
										)
									}
									fullWidth
								/>
								<Button
									variant="outlined"
									color="error"
									onClick={() => removeFounder(index)}
								>
									&times;
								</Button>
							</Box>
						))}
					</Stack>
					<Button type="button" variant="outlined" onClick={addFounder} sx={{ mt: 2 }}>
						+ Добавить учредителя
					</Button>
				</Box>

				<Button variant="contained" color="success" type="submit">
					Создать фирму
				</Button>
			</Box>
		</Container>
	);
}
