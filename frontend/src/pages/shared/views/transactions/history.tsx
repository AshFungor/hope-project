import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { TransactionAPI } from '@app/types/transaction';

const Row: React.FC<{ transaction: TransactionAPI.TransactionRecord }> = ({ transaction }) => {
	let rowClass = '';
	if (transaction.status === 'approved') {
        rowClass = 'table-success';
    } else if (transaction.status === 'rejected') {
        rowClass = 'table-danger';
    }

	return (
		<tr className={rowClass}>
			<td>{transaction.transaction_id}</td>
			<td>{transaction.product}</td>
			{transaction.is_money ? (
				<td colSpan={2}>{transaction.count}</td>
			) : (
				<>
					<td>{transaction.count}</td>
					<td>{transaction.amount}</td>
				</>
			)}
			<td>{transaction.status}</td>
			<td>{transaction.updated_at}</td>
			<td>{transaction.side}</td>
			<td>{transaction.second_side}</td>
		</tr>
	);
};

const Table: React.FC<{ transactions: TransactionAPI.TransactionRecord[] }> = ({ transactions }) => (
	<div className="table-responsive">
		<table className="table table-stripped">
			<thead>
				<tr>
					<th>Номер транзакции</th>
					<th>Товар</th>
					<th>Количество</th>
					<th>Цена</th>
					<th>Статус</th>
					<th>Время</th>
					<th>Сторона сделки</th>
					<th>Вторая сторона сделки</th>
				</tr>
			</thead>
			<tbody>
				{transactions.map((t) => (
					<Row key={t.transaction_id} transaction={t} />
				))}
			</tbody>
		</table>
	</div>
);

const TransactionHistory: React.FC = () => {
	const { accountId } = useParams<{ accountId: string }>();
	const [transactions, setTransactions] = useState<TransactionAPI.TransactionRecord[]>([]);
	const [page, setPage] = useState(0);
	const pageSize = 20;

	useEffect(() => {
		if (!accountId) return;
		TransactionAPI.getTransactionHistory(Number(accountId)).then((data) => {
			setTransactions(data);
		});
	}, [accountId]);

	const paginated = transactions.slice(page * pageSize, (page + 1) * pageSize);

	return (
		<div>
			<div className="text-wrap text-center mb-4">
				<p className="mb-1">
					<strong>Транзакции, выполненные вами</strong>
				</p>
			</div>

			<div className="card" style={{ width: '100%' }}>
				<Table transactions={paginated} />

				<nav aria-label="Page navigation">
					<ul className="pagination justify-content-center">
						<li className={`page-item ${page === 0 ? 'disabled' : ''}`}>
							<button className="page-link" onClick={() => setPage(Math.max(0, page - 1))}>
								<span aria-hidden="true">&laquo;</span>
								<span className="sr-only">Previous</span>
							</button>
						</li>

						<li className={`page-item ${paginated.length < pageSize ? 'disabled' : ''}`}>
							<button className="page-link" onClick={() => setPage(page + 1)}>
								<span className="sr-only">Next</span>
								<span aria-hidden="true">&raquo;</span>
							</button>
						</li>
					</ul>
				</nav>
			</div>
		</div>
	);
};

export default TransactionHistory;
