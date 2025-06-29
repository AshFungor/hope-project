import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { CurrentTransactionsRequest } from "@app/codegen/app/protos/transaction/unpaid";
import { DecideOnTransactionRequest } from "@app/codegen/app/protos/transaction/decide";
import { TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

interface ActiveTransaction {
    transactionId: number;
    product: string;
    count: number;
    amount: number;
    secondSide: number;
}

const ActionButtons: React.FC<{
    onDecide: (status: "ACCEPTED" | "REJECTED") => void;
}> = ({ onDecide }) => (
    <td colSpan={4}>
        <button className="btn btn-success me-2" onClick={() => onDecide("ACCEPTED")}>
            Принять
        </button>
        <button className="btn btn-danger" onClick={() => onDecide("REJECTED")}>
            Отклонить
        </button>
    </td>
);

const TransactionDecisionTable: React.FC<{ accountId: number }> = ({ accountId }) => {
    const [transactions, setTransactions] = useState<ActiveTransaction[]>([]);

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
                secondSide: t.sellerAccount ?? 0
            }))
        );
    };

    useEffect(() => {
        load();
    }, [accountId]);

    const decide = async (transactionId: number, status: "ACCEPTED" | "REJECTED") => {
        const req: DecideOnTransactionRequest = {
            account: transactionId,
            status: status
        };

        const response = await Hope.send(
            Request.create({ decideOnTransaction: req })
        );

        if (response.decideOnTransaction?.status === TxStatus.OK) {
            await load();
        } else {
            alert(`Ошибка при решении: ${response.decideOnTransaction?.status}`);
        }
    };

    return (
        <div className="card" style={{ width: "100%" }}>
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
                            <React.Fragment key={t.transactionId}>
                                <tr>
                                    <td>{t.transactionId}</td>
                                    <td>{t.product}</td>
                                    <td>x{t.count}</td>
                                    <td>{t.amount}</td>
                                    <td>{t.secondSide}</td>
                                </tr>
                                <tr>
                                    <ActionButtons onDecide={(status) => decide(t.transactionId, status)} />
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
