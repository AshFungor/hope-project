import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { PageMode } from "@app/types";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { Transaction, Transaction_Status } from "@app/codegen/app/protos/types/transaction";
import { ViewTransactionsRequest } from "@app/codegen/app/protos/transaction/history";

import { Transaction as TransactionLocal } from "@app/api/sub/transaction";
import { useUser } from "@app/contexts/user";

interface TransactionHistoryProps {
    mode: PageMode;
}

const Row: React.FC<{ transaction: Transaction }> = ({ transaction }) => {
    const t = new TransactionLocal(
        transaction.sellerBankAccountId,
        transaction.customerBankAccountId,
        transaction.product,
        transaction.count,
        transaction.amount,
        transaction.status,
        transaction.transactionId,
        transaction.createdAt,
        transaction.updatedAt,
        transaction.side,
        transaction.isMoney
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
            <td>{t.createdAt}</td>
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
                    <th>Создано</th>
                    <th>Обновлено</th>
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

export default function TransactionHistory({ mode }: TransactionHistoryProps) {
    const params = useParams();
    const { bankAccountId } = useUser();

    const effectiveAccountId =
        mode === PageMode.Company
            ? Number(params.companyId)
            : bankAccountId;

    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [page, setPage] = useState(0);
    const pageSize = 20;

    useEffect(() => {
        if (!effectiveAccountId) return;

        const fetchTransactions = async () => {
            const viewReq: ViewTransactionsRequest = {
                account: effectiveAccountId,
            };

            const response = await Hope.sendTyped(
                Request.create({ viewTransactionHistory: viewReq }),
                "viewTransactionHistory"
            );

            const txs = response.transactions ?? [];
            // Sort transactions by latest first if needed
            setTransactions([...txs].sort((a, b) =>
                (b.updatedAt || "").localeCompare(a.updatedAt || "")
            ));
        };

        fetchTransactions();
    }, [effectiveAccountId]);

    if (!effectiveAccountId) return null;

    const paginated = transactions.slice(page * pageSize, (page + 1) * pageSize);

    return (
        <div>
            <div className="text-wrap text-center mb-4">
                <p className="mb-1">
                    <strong>История транзакций</strong>
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
                                &laquo;
                            </button>
                        </li>

                        <li className={`page-item ${paginated.length < pageSize ? "disabled" : ""}`}>
                            <button
                                className="page-link"
                                onClick={() => setPage(page + 1)}
                            >
                                &raquo;
                            </button>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    );
}
