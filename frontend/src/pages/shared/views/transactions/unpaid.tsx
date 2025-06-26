import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { TransactionAPI } from '@app/types/transaction';

interface ActiveTransaction {
	transaction_id: number;
	product: string;
	count: number;
	amount: number;
	second_side: number;
}

const ActionButtons: React.FC<{
	transactionId: number;
	onDecide: (status: 'approved' | 'rejected') => void;
}> = ({ transactionId, onDecide }) => (
	<td colSpan={4}>
		<button
			className="btn btn-success me-2"
			onClick={() => onDecide('approved')}
		>
			Принять
		</button>
		<button
			className="btn btn-danger"
			onClick={() => onDecide('rejected')}
		>
			Отклонить
		</button>
	</td>
);

const TransactionDecisionTable: React.FC<{ accountId: number }> = ({ accountId }) => {
	const [transactions, setTransactions] = useState<ActiveTransaction[]>([]);

	const load = async () => {
		const data = await TransactionAPI.getActiveProposals(accountId);
		setTransactions(data);
	};

	useEffect(() => {
		load();
	}, [accountId]);

	const decide = async (id: number, status: 'approved' | 'rejected') => {
		try {
			const response = await TransactionAPI.decideOnProposal(id, status);
			if (response.ok) {
				await load(); // reload transactions after decision
			} else {
				alert(`Ошибка: ${await response.text()}`);
			}
		} catch (e) {
			alert(`Ошибка при отправке решения`);
			console.error(e);
		}
	};

	return (
		<div className="card" style={{ width: '100%' }}>
			<div className="text-wrap text-center mb-4">
				<p className="mb-1">
					<strong>Ваши транзакции:</strong>
				</p>
			</div>
			<div className="table-responsive">
				<table className="table table-striped">
					<thead>
						<tr>
							<th>Номер транзакции</th>
							<th>Название</th>
							<th>Количество</th>
							<th>Цена</th>
							<th>Вторая сторона сделки</th>
						</tr>
					</thead>
					<tbody>
						{transactions.map((t) => (
							<React.Fragment key={t.transaction_id}>
								<tr>
									<td>{t.transaction_id}</td>
									<td>{t.product}</td>
									<td>x{t.count}</td>
									<td>{t.amount}</td>
									<td>{t.second_side}</td>
								</tr>
								<tr>
									<ActionButtons
										transactionId={t.transaction_id}
										onDecide={(status) => decide(t.transaction_id, status)}
									/>
								</tr>
							</React.Fragment>
						))}
					</tbody>
				</table>
			</div>
		</div>
	);
};

const TransactionDecisionPage: React.FC = () => {
	const { accountId } = useParams<{ accountId: string }>();
	if (!accountId) return <div>Missing account ID in URL</div>;
	return <TransactionDecisionTable accountId={parseInt(accountId, 10)} />;
};

export default TransactionDecisionPage;
