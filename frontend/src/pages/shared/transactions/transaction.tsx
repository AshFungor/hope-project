import React, { useState } from "react";
import { useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { CreateMoneyTransactionRequest } from "@app/codegen/app/protos/transaction/create";
import { TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

import { PageMode } from "@app/types";
import { useUser } from "@app/contexts/user";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

interface MoneyTransferFormProps {
    mode: PageMode;
}

const MoneyTransferForm: React.FC<MoneyTransferFormProps> = ({ mode }) => {
    const params = useParams();
    const { bankAccountId } = useUser();

    const userBankAccount =
        mode === PageMode.Company
            ? Number(params.companyId)
            : bankAccountId;

    const [sellerAccount, setSellerAccount] = useState("");
    const [amount, setAmount] = useState("");
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    const getStatusMessage = (status: TxStatus | undefined): { contents: string; status: AlertStatus } => {
        switch (status) {
            case TxStatus.OK:
                return { contents: "Перевод успешно отправлен", status: AlertStatus.Info };
            case TxStatus.CUSTOMER_IS_SELLER:
                return { contents: "Ошибка: получатель совпадает с отправителем", status: AlertStatus.Error };
            case TxStatus.ALREADY_PROCESSED:
                return { contents: "Ошибка: транзакция уже обработана", status: AlertStatus.Warning };
            case TxStatus.COUNT_OUT_OF_BOUNDS:
                return { contents: "Ошибка: некорректное количество", status: AlertStatus.Error };
            case TxStatus.AMOUNT_OUT_OF_BOUNDS:
                return { contents: "Ошибка: сумма вне допустимого диапазона", status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING:
                return { contents: "Ошибка: ваш счёт не найден", status: AlertStatus.Error };
            case TxStatus.CUSTOMER_MISSING:
                return { contents: "Ошибка: счёт получателя не найден", status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING_GOODS:
                return { contents: "Ошибка: недостаточно средств на вашем счёте", status: AlertStatus.Error };
            default:
                return { contents: "Неизвестная ошибка при создании перевода", status: AlertStatus.Notice };
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);

        const seller = parseInt(sellerAccount, 10);
        const amt = parseInt(amount, 10);

        if (!userBankAccount || isNaN(seller) || isNaN(amt) || seller <= 0 || amt <= 0) {
            setMessage({
                contents: "Введите корректные значения для счёта и суммы",
                status: AlertStatus.Error,
            });
            return;
        }

        try {
            const moneyTxReq = CreateMoneyTransactionRequest.create({
                sellerAccount: userBankAccount,
                customerAccount: seller,
                amount: amt,
            });

            const response = await Hope.send(
                Request.create({ createMoneyTransaction: moneyTxReq })
            );

            const resultStatus = getStatusMessage(
                response.createTransaction?.status as TxStatus | undefined
            );

            setMessage(resultStatus);

            if (response.createTransaction?.status === TxStatus.OK) {
                setSellerAccount("");
                setAmount("");
            }
        } catch (err) {
            console.error(err);
            setMessage({
                contents: "Ошибка при отправке запроса",
                status: AlertStatus.Error,
            });
        }
    };

    if (!userBankAccount || isNaN(userBankAccount)) {
        return <MessageAlert message="Некорректный ID счёта" status={AlertStatus.Error} />;
    }

    return (
        <form role="form" onSubmit={handleSubmit}>
            <MessageAlert
                message={message?.contents ?? ""}
                status={message?.status ?? AlertStatus.Info}
            />

            <div className="mb-4">
                <p className="mb-1" id="customer-account">
                    <strong>Ваш счёт:</strong> {userBankAccount}
                </p>
            </div>

            <div className="mb-4">
                <label htmlFor="seller-account" className="form-label">
                    <strong>Счёт получателя:</strong>
                </label>
                <input
                    className="form-control text-center"
                    name="seller-account"
                    type="number"
                    placeholder="Введите счёт получателя"
                    value={sellerAccount}
                    onChange={(e) => setSellerAccount(e.target.value)}
                />
            </div>

            <div className="mb-4">
                <label htmlFor="amount" className="form-label">
                    <strong>Сумма:</strong>
                </label>
                <input
                    className="form-control text-center"
                    name="amount"
                    type="number"
                    placeholder="Введите сумму перевода"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                />
            </div>

            <div className="d-grid gap-2 d-mb-block mb-4">
                <button type="submit" className="btn btn-success mb-3">
                    Подтверждаю
                </button>
            </div>
        </form>
    );
};

export default MoneyTransferForm;
