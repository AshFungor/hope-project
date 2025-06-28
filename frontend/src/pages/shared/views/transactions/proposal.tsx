import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { Product } from "@app/codegen/app/protos/types/product";
import { CreateProductTransactionRequest, } from "@app/codegen/app/protos/transaction/create";
import { TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

const NewTransactionForm: React.FC = () => {
    const { accountId } = useParams<{ accountId: string }>();
    const navigate = useNavigate();

    const [sellerAccount, setSellerAccount] = useState("");
    const [productName, setProductName] = useState("");
    const [count, setCount] = useState("");
    const [amount, setAmount] = useState("");
    const [products, setProducts] = useState<Product[]>([]);
    const [messages, setMessages] = useState<string[]>([]);

    const buyerAccount = Number(accountId);

    const getCreateTransactionMessage = (status: TxStatus | undefined): string => {
        switch (status) {
            case TxStatus.OK:
                return "Операция успешно выполнена";
            case TxStatus.CUSTOMER_IS_SELLER:
                return "Ошибка: покупатель и продавец совпадают";
            case TxStatus.ALREADY_PROCESSED:
                return "Ошибка: транзакция уже обработана";
            case TxStatus.COUNT_OUT_OF_BOUNDS:
                return "Ошибка: некорректное количество товара";
            case TxStatus.AMOUNT_OUT_OF_BOUNDS:
                return "Ошибка: некорректная сумма";
            case TxStatus.SELLER_MISSING_GOODS:
                return "Ошибка: у продавца недостаточно товара";
            case TxStatus.CUSTOMER_MISSING_MONEY:
                return "Ошибка: у покупателя недостаточно средств";
            case TxStatus.CUSTOMER_MISSING:
                return "Ошибка: покупатель не найден";
            case TxStatus.SELLER_MISSING:
                return "Ошибка: продавец не найден";
            default:
                return "Неизвестная ошибка";
        }
    };

    useEffect(() => {
        (async () => {
            const response = await Hope.send(Request.create({ allProducts: {} }));
            setProducts(response.allProducts?.products ?? []);
        })();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const createTxReq = CreateProductTransactionRequest.create({
            sellerAccount: buyerAccount,
            customerAccount: Number(sellerAccount),
            product: productName,
            count: Number(count),
            amount: Number(amount),
        });

        const response = await Hope.send(
            Request.create({ createProductTransaction: createTxReq })
        );

        const status = response.createTransaction?.status as TxStatus | undefined;

        if (status === TxStatus.OK) {
            setMessages(["success: " + getCreateTransactionMessage(status)]);
            setTimeout(() => navigate(-1), 1000);
        } else {
            setMessages(["danger: " + getCreateTransactionMessage(status)]);
        }
    };

    return (
        <form role="form" onSubmit={handleSubmit}>
            {messages.map((msg, i) => {
                const [type, text] = msg.split(": ");
                return (
                    <div key={i} className={`alert alert-${type.trim()} fade-in`} role="alert">
                        {text.trim()}
                    </div>
                );
            })}

            <div className="mb-4">
                <p className="mb-1">
                    <strong>Ваш счёт:</strong> {buyerAccount}
                </p>
            </div>

            <div className="mb-4">
                <label className="form-label">
                    <strong>Счёт получателя:</strong>
                </label>
                <input
                    className="form-control text-center"
                    type="number"
                    value={sellerAccount}
                    onChange={(e) => setSellerAccount(e.target.value)}
                    placeholder="Введите счёт получателя"
                />
            </div>

            <div className="mb-4">
                <select
                    className="form-select"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                >
                    <option value="">Выбрать продукт</option>
                    {products
                        .filter((p) => p.name !== "надик")
                        .map((product) => (
                            <option key={product.name} value={product.name}>
                                {product.name}
                            </option>
                        ))}
                </select>
            </div>

            <div className="mb-4">
                <label className="form-label">
                    <strong>Количество товара:</strong>
                </label>
                <input
                    className="form-control text-center"
                    type="number"
                    value={count}
                    onChange={(e) => setCount(e.target.value)}
                    placeholder="Введите количество товара"
                />
            </div>

            <div className="mb-4">
                <label className="form-label">
                    <strong>Цена сделки:</strong>
                </label>
                <input
                    className="form-control text-center"
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="Введите цену сделки"
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

export default NewTransactionForm;
