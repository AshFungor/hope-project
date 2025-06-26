import React, { useState } from 'react';

import { useLocation, useNavigate } from 'react-router-dom';
import { Goal } from '@app/utils/goal';

import BalanceSection from '@app/pages/shared/widgets/balance';

export default function GoalFormPage() {
	const location = useLocation();
	const navigate = useNavigate();

	const params = new URLSearchParams(location.search);
	const current = Number(params.get('current'));
	const bankAccountId = Number(params.get('bank_account_id'));

	const [value, setValue] = useState<number | undefined>();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		await Goal.createGoal(bankAccountId, value ?? null);
		navigate(-1);
	};

	const handleSkip = async () => {
		await Goal.createGoal(bankAccountId, null);
		navigate(-1);
	};

	return (
		<form onSubmit={handleSubmit}>
			<div className="mb-4">
				<p className="mb-1">
					<strong>Ваш счёт:</strong> {bankAccountId}
				</p>
			</div>

			<BalanceSection current={current} />

			<div className="form-group mb-4">
				<input
					className="form-control text-center"
					type="number"
					name="value"
					min="1"
					placeholder="Введите цель на сегодня (в надиках)"
					value={value ?? ''}
					onChange={(e) => setValue(Number(e.target.value))}
				/>
			</div>

			<div className="d-grid gap-2 d-mb-block mb-4">
				<button type="submit" className="btn btn-success btn-sm mb-3">
					Установить цель
				</button>
				<button type="button" className="btn btn-secondary btn-sm" onClick={handleSkip}>
					Пропустить
				</button>
			</div>
		</form>
	);
}
