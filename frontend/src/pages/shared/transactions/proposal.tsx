import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { Product } from "@app/codegen/app/protos/types/product";
import { CreateProductTransactionRequest } from "@app/codegen/app/protos/transaction/create";
import { TransactionStatusReason as TxStatus } from "@app/codegen/app/protos/types/transaction";

import { useUser } from "@app/contexts/user";
import { PageMode } from "@app/types";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

interface NewTransactionFormProps {
    mode: PageMode;
}

const NewTransactionForm: React.FC<NewTransactionFormProps> = ({ mode }) => {
    const params = useParams();
    const { bankAccountId } = useUser();
    const navigate = useNavigate();

    const effectiveAccountId =
        mode === PageMode.Company
            ? Number(params.companyId)
            : bankAccountId;

    const [sellerAccount, setSellerAccount] = useState("");
    const [productName, setProductName] = useState("");
    const [count, setCount] = useState("");
    const [amount, setAmount] = useState("");
    const [products, setProducts] = useState<Product[]>([]);
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    const getCreateTransactionStatus = (status: TxStatus | undefined): { contents: string; status: AlertStatus } => {
        switch (status) {
            case TxStatus.OK:
                return { contents: "Операция успешно выполнена", status: AlertStatus.Info };
            case TxStatus.CUSTOMER_IS_SELLER:
                return { contents: "Ошибка: покупатель и продавец совпадают", status: AlertStatus.Error };
            case TxStatus.ALREADY_PROCESSED:
                return { contents: "Ошибка: транзакция уже обработана", status: AlertStatus.Warning };
            case TxStatus.COUNT_OUT_OF_BOUNDS:
                return { contents: "Ошибка: некорректное количество товара", status: AlertStatus.Error };
            case TxStatus.AMOUNT_OUT_OF_BOUNDS:
                return { contents: "Ошибка: некорректная сумма", status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING_GOODS:
                return { contents: "Ошибка: у продавца недостаточно товара", status: AlertStatus.Error };
            case TxStatus.CUSTOMER_MISSING_MONEY:
                return { contents: "Ошибка: у покупателя недостаточно средств", status: AlertStatus.Error };
            case TxStatus.CUSTOMER_MISSING:
                return { contents: "Ошибка: покупатель не найден", status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING:
                return { contents: "Ошибка: продавец не найден", status: AlertStatus.Error };
            default:
                return { contents: "Неизвестная ошибка", status: AlertStatus.Notice };
        }
    };

    useEffect(() => {
        const fetchProducts = async () => {
            const result = await Hope.sendTyped(
                Request.create({ allProducts: {} }),
                "allProducts"
            );
            setProducts(result.products ?? []);
        };

        fetchProducts();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!effectiveAccountId) {
            setMessage({ contents: "Ошибка: не определён аккаунт", status: AlertStatus.Error });
            return;
        }

        const createTxReq = CreateProductTransactionRequest.create({
            customerBankAccountId: Number(sellerAccount),
            sellerBankAccountId: effectiveAccountId,
            product: productName,
            count: Number(count),
            amount: Number(amount),
        });

        const result = await Hope.sendTyped(
            Request.create({ createProductTransaction: createTxReq }),
            "createProductTransaction"
        );

        const resultStatus = getCreateTransactionStatus(result.status as TxStatus | undefined);
        setMessage(resultStatus);

        if (result.status === TxStatus.OK) {
            setTimeout(() => navigate(-1), 1000);
        }
    };

    if (!effectiveAccountId) {
        return <MessageAlert message="Не удалось определить аккаунт" status={AlertStatus.Error} />;
    }

    return (
        <form role="form" onSubmit={handleSubmit}>
            <MessageAlert
                message={message?.contents ?? ""}
                status={message?.status ?? AlertStatus.Info}
            />

            <div className="mb-4">
                <p className="mb-1">
                    <strong>Ваш счёт:</strong> {effectiveAccountId}
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
