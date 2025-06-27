import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { TransactionAPI } from '@app/types/transaction';

const MoneyTransferForm: React.FC = () => {
	const { accountId } = useParams<{ accountId: string }>();
	const userBankAccount = Number(accountId);

	const [sellerAccount, setSellerAccount] = useState('');
	const [amount, setAmount] = useState('');
	const [message, setMessage] = useState<string | null>(null);
	const [messageType, setMessageType] = useState<'success' | 'danger'>('success');

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setMessage(null);

		const seller = parseInt(sellerAccount, 10);
		const amt = parseInt(amount, 10);
		if (isNaN(seller) || isNaN(amt) || seller <= 0 || amt <= 0) {
			setMessageType('danger');
			setMessage('Введите корректные значения');
			return;
		}

		try {
			const response = await TransactionAPI.createMoneyProposal(
				seller,
				userBankAccount,
				amt
			);
			if (!response.ok) {
				const text = await response.text();
				setMessageType('danger');
				setMessage(`Ошибка: ${text}`);
			} else {
				setMessageType('success');
				setMessage('Перевод отправлен');
				setSellerAccount('');
				setAmount('');
			}
		} catch (err) {
			setMessageType('danger');
			setMessage('Ошибка при отправке запроса');
			console.error(err);
		}
	};

	if (isNaN(userBankAccount)) {
		return <div>Некорректный ID счёта в URL</div>;
	}

	return (
		<form role="form" onSubmit={handleSubmit}>
			{message && (
				<ul className="flashes">
					<li className={`text-${messageType} text-center`}>{message}</li>
				</ul>
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
