import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { CurrentTransactionsRequest } from '@app/codegen/app/protos/transaction/unpaid';
import {
	DecideOnTransactionRequest,
	DecideOnTransactionRequest_Status,
} from '@app/codegen/app/protos/transaction/decide';
import {
	TransactionStatusReason,
	TransactionStatusReason as TxStatus,
} from '@app/codegen/app/protos/types/transaction';

import { PageMode } from '@app/types';
import { useUser } from '@app/contexts/user';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

interface ActiveTransaction {
	transactionId: number;
	product: string;
	count: number;
	amount: number;
	secondSide: number;
}

const ActionButtons: React.FC<{
	onDecide: (status: DecideOnTransactionRequest_Status) => void;
}> = ({ onDecide }) => (
	<TableRow>
		<TableCell colSpan={5}>
			<Stack direction="row" spacing={2}>
				<Button
					variant="contained"
					color="success"
					onClick={() => onDecide(DecideOnTransactionRequest_Status.ACCEPTED)}
				>
					Принять
				</Button>
				<Button
					variant="contained"
					color="error"
					onClick={() => onDecide(DecideOnTransactionRequest_Status.REJECTED)}
				>
					Отклонить
				</Button>
			</Stack>
		</TableCell>
	</TableRow>
);

const TransactionDecisionTable: React.FC<{ accountId: number }> = ({ accountId }) => {
	const [transactions, setTransactions] = useState<ActiveTransaction[]>([]);
	const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

	const load = async () => {
		const req: CurrentTransactionsRequest = { account: accountId };
		const response = await Hope.send(Request.create({ currentTransactions: req }));
		const data = response.currentTransactions?.transactions ?? [];

		setTransactions(
			data.map((t) => ({
				transactionId: t.transactionId,
				product: t.product,
				count: t.count,
				amount: t.amount,
				secondSide: t.sellerBankAccountId ?? 0,
			}))
		);
	};

	useEffect(() => {
		load();
	}, [accountId]);

	const getTransactionStatusMessage = function (status: TransactionStatusReason): {
		contents: string;
		status: AlertStatus;
	} {
		switch (status) {
			case TransactionStatusReason.OK:
				return { contents: 'Транзакция успешно обработана.', status: AlertStatus.Info };
			case TransactionStatusReason.CUSTOMER_IS_SELLER:
				return { contents: 'Покупатель и продавец совпадают.', status: AlertStatus.Error };
			case TransactionStatusReason.ALREADY_PROCESSED:
				return { contents: 'Транзакция уже была обработана.', status: AlertStatus.Error };
			case TransactionStatusReason.COUNT_OUT_OF_BOUNDS:
				return {
					contents: 'Количество товара превышает доступное.',
					status: AlertStatus.Error,
				};
			case TransactionStatusReason.AMOUNT_OUT_OF_BOUNDS:
				return {
					contents: 'Сумма транзакции выходит за допустимые пределы.',
					status: AlertStatus.Error,
				};
			case TransactionStatusReason.SELLER_MISSING_GOODS:
				return { contents: 'У продавца недостаточно товаров.', status: AlertStatus.Error };
			case TransactionStatusReason.CUSTOMER_MISSING_MONEY:
				return {
					contents: 'У покупателя недостаточно средств.',
					status: AlertStatus.Error,
				};
			case TransactionStatusReason.CUSTOMER_MISSING:
				return { contents: 'Покупатель не найден.', status: AlertStatus.Error };
			case TransactionStatusReason.SELLER_MISSING:
				return { contents: 'Продавец не найден.', status: AlertStatus.Error };
			case TransactionStatusReason.MULTIPLE_PRODUCTS:
				return {
					contents: 'Транзакция не поддерживает несколько товаров одновременно.',
					status: AlertStatus.Error,
				};
			case TransactionStatusReason.PREFECTURES_DO_NOT_MATCH:
				return {
					contents:
						'Транзакция не может быть совершена между компанией и покупателем в разных префектурах',
					status: AlertStatus.Error,
				};
			default:
				return {
					contents: `Неизвестный статус транзакции (${status})`,
					status: AlertStatus.Error,
				};
		}
	};

	const decide = async (transactionId: number, status: DecideOnTransactionRequest_Status) => {
		const req: DecideOnTransactionRequest = {
			id: transactionId,
			status: status,
		};

		const response = await Hope.send(Request.create({ decideOnTransaction: req }));

		if (response.decideOnTransaction?.status === TxStatus.OK) {
			setMessage({
				contents: `Транзакция ${transactionId} обновлена`,
				status: AlertStatus.Info,
			});
			await load();
		} else {
			const fallback = getTransactionStatusMessage(
				response.decideOnTransaction?.status ?? TxStatus.UNRECOGNIZED
			);
			setMessage(fallback);
		}
	};

	return (
		<Paper sx={{ width: '100%', overflow: 'auto', p: 2 }}>
			{message && <MessageAlert message={message.contents} status={message.status} />}

			<Typography variant="h5" align="center" gutterBottom>
				Ваши транзакции
			</Typography>

			<Table>
				<TableHead>
					<TableRow>
						<TableCell>Номер транзакции</TableCell>
						<TableCell>Название</TableCell>
						<TableCell>Количество</TableCell>
						<TableCell>Цена</TableCell>
						<TableCell>Вторая сторона сделки</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					{transactions.map((t) => (
						<React.Fragment key={t.transactionId}>
							<TableRow>
								<TableCell>{t.transactionId}</TableCell>
								<TableCell>{t.product}</TableCell>
								<TableCell>x{t.count}</TableCell>
								<TableCell>{t.amount}</TableCell>
								<TableCell>{t.secondSide}</TableCell>
							</TableRow>
							<ActionButtons onDecide={(status) => decide(t.transactionId, status)} />
						</React.Fragment>
					))}
				</TableBody>
			</Table>
		</Paper>
	);
};

interface TransactionDecisionPageProps {
	mode: PageMode;
}

const TransactionDecisionPage: React.FC<TransactionDecisionPageProps> = ({ mode }) => {
	const params = useParams();
	const { bankAccountId } = useUser();

	const effectiveAccountId = mode === PageMode.Org ? Number(params.orgId) : bankAccountId;

	if (!effectiveAccountId) {
		return <Typography>Missing account ID</Typography>;
	}

	return (
		<Container sx={{ mt: 4 }}>
			<TransactionDecisionTable accountId={effectiveAccountId} />
		</Container>
	);
};

export default TransactionDecisionPage;
