import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { TransactionAPI } from '@app/types/transaction';
import { ProductAPI, types as ProductTypes } from '@app/types/product';

const NewTransactionForm: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const [sellerAccount, setSellerAccount] = useState('');
    const [productName, setProductName] = useState('');
    const [count, setCount] = useState('');
    const [amount, setAmount] = useState('');
    const [products, setProducts] = useState<ProductTypes.Product[]>([]);
    const [messages, setMessages] = useState<string[]>([]);

    const buyerAccount = Number(id); // taken from the URL directly

    useEffect(() => {
        ProductAPI.all().then(setProducts);
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const res = await TransactionAPI.createProductProposal(
            Number(sellerAccount),
            buyerAccount,
            productName,
            Number(count),
            Number(amount)
        );

        if (res.ok) {
            setMessages(['success: Транзакция успешно создана']);
            setTimeout(() => navigate(-1), 1000);
        } else {
            setMessages(['danger: Ошибка при создании транзакции']);
        }
    };

    return (
        <form role="form" onSubmit={handleSubmit}>
            {messages.map((msg, i) => {
                const [type, text] = msg.split(': ');
                return (
                    <div key={i} className={`alert alert-${type.trim()} fade-in`} role="alert">
                        {text.trim()}
                    </div>
                );
            })}

            <div className="mb-4">
                <p className="mb-1" id="customer-account">
                    <strong>Ваш счёт:</strong> {buyerAccount}
                </p>
            </div>

            <div className="mb-4">
                <label className="form-label">
                    <strong>Счёт получателя:</strong>
                </label>
                <input
                    className="form-control text-center"
                    name="seller-account"
                    type="number"
                    value={sellerAccount}
                    onChange={(e) => setSellerAccount(e.target.value)}
                    placeholder="Введите счёт получателя"
                />
            </div>

            <div className="mb-4">
                <select
                    className="form-select"
                    name="product-name"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                >
                    <option value="">Выбрать продукт</option>
                    {products
                        .filter((p) => p.name !== 'надик')
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
                    name="count"
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
                    name="amount"
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
