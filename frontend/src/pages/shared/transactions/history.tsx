import React, { useEffect, useState } from "react";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { Transaction, Transaction_Status } from "@app/codegen/app/protos/types/transaction";
import { ViewTransactionsRequest, ViewTransactionsResponse } from "@app/codegen/app/protos/transaction/history";

import { Transaction as TransactionLocal } from "@app/api/sub/transaction";
import { useEffectiveId } from "@app/contexts/abstract/current-bank-account";

const Row: React.FC<{ transaction: Transaction }> = ({ transaction }) => {
    const t = new TransactionLocal(
        transaction.sellerAccount,
        transaction.customerAccount,
        transaction.product,
        transaction.count,
        transaction.amount,
        transaction.status,
        transaction.transactionId,
        transaction.updatedAt,
        transaction.side,
        transaction.isMoney,
    );

    let rowClass = "";
    if (transaction.status === Transaction_Status.ACCEPTED) {
        rowClass = "table-success";
    } else if (transaction.status === Transaction_Status.REJECTED) {
        rowClass = "table-danger";
    }

    return (
        <tr className={rowClass}>
            <td>{t.transactionId}</td>
            <td>{t.product}</td>
            {t.isMoney ? (
                <td colSpan={2}>{t.count}</td>
            ) : (
                <>
                    <td>{t.count}</td>
                    <td>{t.amount}</td>
                </>
            )}
            <td>{t.stringStatus()}</td>
            <td>{t.updatedAt}</td>
            <td>{t.side}</td>
        </tr>
    );
};

const Table: React.FC<{ transactions: Transaction[] }> = ({ transactions }) => (
    <div className="table-responsive">
        <table className="table table-striped">
            <thead>
                <tr>
                    <th>Номер транзакции</th>
                    <th>Товар</th>
                    <th>Количество</th>
                    <th>Цена</th>
                    <th>Статус</th>
                    <th>Время</th>
                    <th>Сторона сделки</th>
                </tr>
            </thead>
            <tbody>
                {transactions.map((t) => (
                    <Row key={t.transactionId} transaction={t} />
                ))}
            </tbody>
        </table>
    </div>
);

const TransactionHistory: React.FC = () => {
    const { id: effectiveAccountId } = useEffectiveId();
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [page, setPage] = useState(0);
    const pageSize = 20;

    useEffect(() => {
        if (!effectiveAccountId) {
			return;
		}

        const fetchTransactions = async () => {
            const viewReq: ViewTransactionsRequest = {
                account: effectiveAccountId,
            };

            const response = await Hope.sendTyped(
				Request.create({ viewTransactionHistory: viewReq }),
				"viewTransactionHistory"
			);
            setTransactions(response.transactions);
        };

        fetchTransactions();
    }, [effectiveAccountId]);

	
    if (!effectiveAccountId) {
		return null;
	}
	
	const paginated = transactions.slice(page * pageSize, (page + 1) * pageSize);
    return (
        <div>
            <div className="text-wrap text-center mb-4">
                <p className="mb-1">
                    <strong>Транзакции, выполненные вами</strong>
                </p>
            </div>

            <div className="card" style={{ width: "100%" }}>
                <Table transactions={paginated} />

                <nav aria-label="Page navigation">
                    <ul className="pagination justify-content-center">
                        <li className={`page-item ${page === 0 ? "disabled" : ""}`}>
                            <button
                                className="page-link"
                                onClick={() => setPage(Math.max(0, page - 1))}
                            >
                                <span aria-hidden="true">&laquo;</span>
                                <span className="sr-only">Previous</span>
                            </button>
                        </li>

                        <li className={`page-item ${paginated.length < pageSize ? "disabled" : ""}`}>
                            <button
                                className="page-link"
                                onClick={() => setPage(page + 1)}
                            >
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
