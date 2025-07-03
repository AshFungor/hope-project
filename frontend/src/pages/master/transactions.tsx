import React, { useEffect, useState } from 'react';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import {
	MasterAddMoneyRequest,
	MasterAddProductRequest,
	MasterRemoveMoneyRequest,
	MasterRemoveProductRequest,
} from '@app/codegen/app/protos/transaction/master';

import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Autocomplete from '@mui/material/Autocomplete';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

const TransactionStatusReasonLabels: Record<number, string> = {
	0: 'Операция выполнена успешно',
	1: 'Покупатель и продавец совпадают',
	2: 'Транзакция уже обработана',
	3: 'Количество выходит за пределы',
	4: 'Сумма выходит за пределы',
	5: 'У продавца нет товара',
	6: 'У покупателя недостаточно денег',
	7: 'Покупатель отсутствует',
	8: 'Продавец отсутствует',
	9: 'Найдено несколько продуктов',
	10: 'Префектуры не совпадают',
};

const MasterActionsPage: React.FC = () => {
	const [products, setProducts] = useState<string[]>([]);
	const [expanded, setExpanded] = useState<string | false>(false);

	const [removeMoneyAccount, setRemoveMoneyAccount] = useState('');
	const [removeMoneyAmount, setRemoveMoneyAmount] = useState('');

	const [addMoneyAccount, setAddMoneyAccount] = useState('');
	const [addMoneyAmount, setAddMoneyAmount] = useState('');

	const [removeProductAccount, setRemoveProductAccount] = useState('');
	const [removeProductName, setRemoveProductName] = useState('');
	const [removeProductCount, setRemoveProductCount] = useState('');
	const [removeProductAmount, setRemoveProductAmount] = useState('');

	const [addProductAccount, setAddProductAccount] = useState('');
	const [addProductName, setAddProductName] = useState('');
	const [addProductCount, setAddProductCount] = useState('');
	const [addProductAmount, setAddProductAmount] = useState('');

	const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

	useEffect(() => {
		(async () => {
			const response = await Hope.send(Request.create({ allProducts: {} }));
			const names = response.allProducts?.products?.map((p) => p.name) ?? [];
			setProducts(names);
		})();
	}, []);

	const handleChange = (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
		setExpanded(isExpanded ? panel : false);
		setMessage(null);
	};

	const handleMoney = async (action: 'remove' | 'add') => {
		try {
			const account = action === 'remove' ? removeMoneyAccount : addMoneyAccount;
			const amount = action === 'remove' ? removeMoneyAmount : addMoneyAmount;

			const req =
				action === 'remove'
					? MasterRemoveMoneyRequest.create({
							customerBankAccountId: Number(account),
							amount: Number(amount),
						})
					: MasterAddMoneyRequest.create({
							customerBankAccountId: Number(account),
							amount: Number(amount),
						});

			const request = Request.create(
				action === 'remove' ? { masterRemoveMoney: req } : { masterAddMoney: req }
			);

			const response = await Hope.send(request);

			const status = response.createMoneyTransaction?.status;

			const messageText = TransactionStatusReasonLabels[status ?? -1] || 'Неизвестная ошибка';
			const statusType = status === 0 ? AlertStatus.Info : AlertStatus.Error;

			setMessage({ contents: messageText, status: statusType });

			if (status === 0) {
				if (action === 'remove') {
					setRemoveMoneyAccount('');
					setRemoveMoneyAmount('');
				} else {
					setAddMoneyAccount('');
					setAddMoneyAmount('');
				}
			}
		} catch (err) {
			console.error(err);
			setMessage({
				contents: `Ошибка при выполнении операции '${action}' надики`,
				status: AlertStatus.Error,
			});
		}
	};

	const handleProduct = async (action: 'remove' | 'add') => {
		try {
			const account = action === 'remove' ? removeProductAccount : addProductAccount;
			const product = action === 'remove' ? removeProductName : addProductName;
			const count = action === 'remove' ? removeProductCount : addProductCount;
			const amount = action === 'remove' ? removeProductAmount : addProductAmount;

			const req =
				action === 'remove'
					? MasterRemoveProductRequest.create({
							customerBankAccountId: Number(account),
							product: product,
							count: Number(count),
							amount: Number(amount),
						})
					: MasterAddProductRequest.create({
							customerBankAccountId: Number(account),
							product: product,
							count: Number(count),
							amount: Number(amount),
						});

			const request = Request.create(
				action === 'remove' ? { masterRemoveProduct: req } : { masterAddProduct: req }
			);

			const response = await Hope.send(request);

			const status = response.createProductTransaction?.status;

			const messageText = TransactionStatusReasonLabels[status ?? -1] || 'Неизвестная ошибка';
			const statusType = status === 0 ? AlertStatus.Info : AlertStatus.Error;

			setMessage({ contents: messageText, status: statusType });

			if (status === 0) {
				if (action === 'remove') {
					setRemoveProductAccount('');
					setRemoveProductName('');
					setRemoveProductCount('');
					setRemoveProductAmount('');
				} else {
					setAddProductAccount('');
					setAddProductName('');
					setAddProductCount('');
					setAddProductAmount('');
				}
			}
		} catch (err) {
			console.error(err);
			setMessage({
				contents: `Ошибка при выполнении операции '${action}' товар`,
				status: AlertStatus.Error,
			});
		}
	};

	return (
		<Box sx={{ maxWidth: 500, mx: 'auto', mt: 4 }}>
			{message && <MessageAlert message={message.contents} status={message.status} />}

			<Accordion expanded={expanded === 'panel1'} onChange={handleChange('panel1')}>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>Списать надики</AccordionSummary>
				<AccordionDetails>
					<TextField
						label="Счет"
						value={removeMoneyAccount}
						onChange={(e) => setRemoveMoneyAccount(e.target.value)}
						fullWidth
						helperText="Номер банковского счета"
						sx={{ mb: 3 }}
					/>
					<TextField
						label="Количество"
						value={removeMoneyAmount}
						onChange={(e) => setRemoveMoneyAmount(e.target.value)}
						fullWidth
						helperText="Сколько надиков списать"
						sx={{ mb: 3 }}
					/>
					<Button variant="contained" fullWidth onClick={() => handleMoney('remove')}>
						Подтверждаю
					</Button>
				</AccordionDetails>
			</Accordion>

			<Accordion expanded={expanded === 'panel2'} onChange={handleChange('panel2')}>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>Добавить надики</AccordionSummary>
				<AccordionDetails>
					<TextField
						label="Счет"
						value={addMoneyAccount}
						onChange={(e) => setAddMoneyAccount(e.target.value)}
						fullWidth
						helperText="Номер банковского счета"
						sx={{ mb: 3 }}
					/>
					<TextField
						label="Количество"
						value={addMoneyAmount}
						onChange={(e) => setAddMoneyAmount(e.target.value)}
						fullWidth
						helperText="Сколько надиков добавить"
						sx={{ mb: 3 }}
					/>
					<Button variant="contained" fullWidth onClick={() => handleMoney('add')}>
						Подтверждаю
					</Button>
				</AccordionDetails>
			</Accordion>

			<Accordion expanded={expanded === 'panel3'} onChange={handleChange('panel3')}>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>Списать товар</AccordionSummary>
				<AccordionDetails>
					<TextField
						label="Счет"
						value={removeProductAccount}
						onChange={(e) => setRemoveProductAccount(e.target.value)}
						fullWidth
						helperText="Номер банковского счета"
						sx={{ mb: 3 }}
					/>
					<Autocomplete
						freeSolo
						options={products}
						inputValue={removeProductName}
						onInputChange={(_, newValue) => setRemoveProductName(newValue)}
						renderInput={(params) => (
							<TextField
								{...params}
								label="Название продукта"
								helperText="Название существующего продукта"
								fullWidth
								sx={{ mb: 3 }}
							/>
						)}
					/>
					<TextField
						label="Количество"
						value={removeProductCount}
						onChange={(e) => setRemoveProductCount(e.target.value)}
						fullWidth
						helperText="Сколько списать"
						sx={{ mb: 3 }}
					/>
					<TextField
						label="Стоимость"
						value={removeProductAmount}
						onChange={(e) => setRemoveProductAmount(e.target.value)}
						fullWidth
						helperText="Сумма, если есть"
						sx={{ mb: 3 }}
					/>
					<Button variant="contained" fullWidth onClick={() => handleProduct('remove')}>
						Подтверждаю
					</Button>
				</AccordionDetails>
			</Accordion>

			<Accordion expanded={expanded === 'panel4'} onChange={handleChange('panel4')}>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>Добавить товар</AccordionSummary>
				<AccordionDetails>
					<TextField
						label="Счет"
						value={addProductAccount}
						onChange={(e) => setAddProductAccount(e.target.value)}
						fullWidth
						helperText="Номер банковского счета"
						sx={{ mb: 3 }}
					/>
					<Autocomplete
						freeSolo
						options={products}
						inputValue={addProductName}
						onInputChange={(_, newValue) => setAddProductName(newValue)}
						renderInput={(params) => (
							<TextField
								{...params}
								label="Название товара"
								helperText="Название существующего товара"
								fullWidth
								sx={{ mb: 3 }}
							/>
						)}
					/>
					<TextField
						label="Количество"
						value={addProductCount}
						onChange={(e) => setAddProductCount(e.target.value)}
						fullWidth
						helperText="Сколько добавить"
						sx={{ mb: 3 }}
					/>
					<TextField
						label="Стоимость"
						value={addProductAmount}
						onChange={(e) => setAddProductAmount(e.target.value)}
						fullWidth
						helperText="Сумма, если есть"
						sx={{ mb: 3 }}
					/>
					<Button variant="contained" fullWidth onClick={() => handleProduct('add')}>
						Подтверждаю
					</Button>
				</AccordionDetails>
			</Accordion>
		</Box>
	);
};

export default MasterActionsPage;
