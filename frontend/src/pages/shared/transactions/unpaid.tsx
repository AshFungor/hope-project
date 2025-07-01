import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import {
    CurrentTransactionsRequest
} from "@app/codegen/app/protos/transaction/unpaid";
import {
    DecideOnTransactionRequest,
    DecideOnTransactionRequest_Status
} from "@app/codegen/app/protos/transaction/decide";
import { TransactionStatusReason, TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

import { PageMode } from "@app/types";
import { useUser } from "@app/contexts/user";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

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
    <td colSpan={4}>
        <button
            className="btn btn-success me-2"
            onClick={() => onDecide(DecideOnTransactionRequest_Status.ACCEPTED)}
        >
            Принять
        </button>
        <button
            className="btn btn-danger"
            onClick={() => onDecide(DecideOnTransactionRequest_Status.REJECTED)}
        >
            Отклонить
        </button>
    </td>
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
                secondSide: t.sellerBankAccountId ?? 0
            }))
        );
    };

    useEffect(() => {
        load();
    }, [accountId]);

    const getTransactionStatusMessage = function (status: TransactionStatusReason): { contents: string; status: AlertStatus } {
        switch (status) {
            case TransactionStatusReason.OK:
                return { contents: "Транзакция успешно обработана.", status: AlertStatus.Info };
            case TransactionStatusReason.CUSTOMER_IS_SELLER:
                return { contents: "Покупатель и продавец совпадают.", status: AlertStatus.Error };
            case TransactionStatusReason.ALREADY_PROCESSED:
                return { contents: "Транзакция уже была обработана.", status: AlertStatus.Error };
            case TransactionStatusReason.COUNT_OUT_OF_BOUNDS:
                return { contents: "Количество товара превышает доступное.", status: AlertStatus.Error };
            case TransactionStatusReason.AMOUNT_OUT_OF_BOUNDS:
                return { contents: "Сумма транзакции выходит за допустимые пределы.", status: AlertStatus.Error };
            case TransactionStatusReason.SELLER_MISSING_GOODS:
                return { contents: "У продавца недостаточно товаров.", status: AlertStatus.Error };
            case TransactionStatusReason.CUSTOMER_MISSING_MONEY:
                return { contents: "У покупателя недостаточно средств.", status: AlertStatus.Error };
            case TransactionStatusReason.CUSTOMER_MISSING:
                return { contents: "Покупатель не найден.", status: AlertStatus.Error };
            case TransactionStatusReason.SELLER_MISSING:
                return { contents: "Продавец не найден.", status: AlertStatus.Error };
            case TransactionStatusReason.MULTIPLE_PRODUCTS:
                return { contents: "Транзакция не поддерживает несколько товаров одновременно.", status: AlertStatus.Error };
            default:
                return { contents: `Неизвестный статус транзакции (${status})`, status: AlertStatus.Error };
        }
    }

    const decide = async (transactionId: number, status: DecideOnTransactionRequest_Status) => {
        const req: DecideOnTransactionRequest = {
            id: transactionId,
            status: status
        };

        const response = await Hope.send(
            Request.create({ decideOnTransaction: req })
        );

        if (response.decideOnTransaction?.status === TxStatus.OK) {
            setMessage({
                contents: `Транзакция ${transactionId} обновлена`,
                status: AlertStatus.Info
            });
            await load();
        } else {
            setMessage({
                contents: `Ошибка при решении: ${response.decideOnTransaction?.status}`,
                status: AlertStatus.Error
            });
        }
    };

    return (
        <div className="card" style={{ width: "100%" }}>
            {message && (
                <MessageAlert
                    message={message.contents}
                    status={message.status}
                />
            )}

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

interface TransactionDecisionPageProps {
    mode: PageMode;
}

const TransactionDecisionPage: React.FC<TransactionDecisionPageProps> = ({ mode }) => {
    const params = useParams();
    const { bankAccountId } = useUser();

    const effectiveAccountId =
        mode === PageMode.Company
            ? Number(params.companyId)
            : bankAccountId;

    if (!effectiveAccountId) {
        return <div>Missing account ID</div>;
    }

    return <TransactionDecisionTable accountId={effectiveAccountId} />;
};

export default TransactionDecisionPage;
