import React, { useState } from "react";
import { useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { CreateMoneyTransactionRequest } from "@app/codegen/app/protos/transaction/create";
import { TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

const MoneyTransferForm: React.FC = () => {
    const { accountId } = useParams<{ accountId: string }>();
    const userBankAccount = Number(accountId);

    const [sellerAccount, setSellerAccount] = useState("");
    const [amount, setAmount] = useState("");
    const [message, setMessage] = useState<string | null>(null);
    const [messageType, setMessageType] = useState<"success" | "danger">("success");

    const getStatusMessage = (status: TxStatus | undefined): string => {
        switch (status) {
            case TxStatus.OK:
                return "Перевод успешно отправлен";
            case TxStatus.CUSTOMER_IS_SELLER:
                return "Ошибка: получатель совпадает с отправителем";
            case TxStatus.ALREADY_PROCESSED:
                return "Ошибка: транзакция уже обработана";
            case TxStatus.COUNT_OUT_OF_BOUNDS:
                return "Ошибка: некорректное количество";
            case TxStatus.AMOUNT_OUT_OF_BOUNDS:
                return "Ошибка: сумма вне допустимого диапазона";
            case TxStatus.SELLER_MISSING:
				return "Ошибка: ваш счёт не найден";
			case TxStatus.CUSTOMER_MISSING:
                return "Ошибка: счёт получателя не найден";
            case TxStatus.SELLER_MISSING_GOODS:
                return "Ошибка: недостаточно средств на вашем счёте";
            default:
                return "Неизвестная ошибка при создании перевода";
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);

        const seller = parseInt(sellerAccount, 10);
        const amt = parseInt(amount, 10);

        if (isNaN(seller) || isNaN(amt) || seller <= 0 || amt <= 0) {
            setMessageType("danger");
            setMessage("Введите корректные значения для счёта и суммы");
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

            const status = response.createTransaction?.status as TxStatus | undefined;

            if (status === TxStatus.OK) {
                setMessageType("success");
                setMessage(getStatusMessage(status));
                setSellerAccount("");
                setAmount("");
            } else {
                setMessageType("danger");
                setMessage(getStatusMessage(status));
            }
        } catch (err) {
            console.error(err);
            setMessageType("danger");
            setMessage("Ошибка при отправке запроса");
        }
    };

    if (isNaN(userBankAccount)) {
        return <div>Некорректный ID счёта в URL</div>;
    }

    return (
        <form role="form" onSubmit={handleSubmit}>
			{message && (
				<div className={`text-${messageType} alert-${messageType} alert fade-in`} role="alert">
					{message}
				</div>
			)}

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
