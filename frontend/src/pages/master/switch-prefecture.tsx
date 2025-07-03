import React, { useState, useEffect } from 'react';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

interface Prefecture {
	id: number;
	name: string;
}

export default function SwitchPrefecturePage() {
	const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
	const [bankAccountId, setBankAccountId] = useState('');
	const [prefectureId, setPrefectureId] = useState('');
	const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

	useEffect(() => {
		(async () => {
			try {
				const response = await Hope.send(Request.create({ allPrefectures: {} }));
				const data = response.allPrefectures?.prefectures ?? [];
				setPrefectures(
					data.map((p, index) => ({
						id: Number(p.bankAccountId),
						name: p.name || `Префектура ${index + 1}`,
					}))
				);
			} catch (err) {
				console.error('failed to query prefectures:', err);
			}
		})();
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		const accountId = parseInt(bankAccountId, 10);
		const prefId = parseInt(prefectureId, 10);

		if (isNaN(accountId) || isNaN(prefId)) {
			setMessage({
				contents: 'Введите корректные значения.',
				status: AlertStatus.Error,
			});
			return;
		}

		const req = Request.create({
			updatePrefectureLink: {
				bankAccountId: accountId,
				prefectureId: prefId,
			},
		});

		const response = await Hope.send(req);

		if (response.updatePrefectureLink?.success) {
			setMessage({
				contents: `Привязка счета ${accountId} к префектуре ${prefId} выполнена.`,
				status: AlertStatus.Info,
			});
			setBankAccountId('');
			setPrefectureId('');
		} else {
			setMessage({
				contents: 'Не удалось выполнить привязку. Проверьте данные.',
				status: AlertStatus.Error,
			});
		}
	};

	return (
		<Container sx={{ mt: 4 }}>
			<Typography variant="h4" align="center" gutterBottom>
				Смена префектуры
			</Typography>

			{message && <MessageAlert message={message.contents} status={message.status} />}

			<Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
				<Stack spacing={3}>
					<TextField
						label="Номер банковского счета"
						type="number"
						value={bankAccountId}
						onChange={(e) => setBankAccountId(e.target.value)}
						placeholder="Введите номер счета"
						fullWidth
					/>

					<FormControl fullWidth>
						<InputLabel id="prefecture-label">Префектура</InputLabel>
						<Select
							labelId="prefecture-label"
							value={prefectureId}
							label="Префектура"
							onChange={(e) => setPrefectureId(e.target.value)}
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
					</FormControl>

					<Button type="submit" variant="contained" color="success" fullWidth>
						Сохранить
					</Button>
				</Stack>
			</Box>
		</Container>
	);
}
