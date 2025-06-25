import { useEffect, useState } from 'react';
import { Accordion, Table, ProgressBar } from 'react-bootstrap';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { useUser } from '@app/contexts/user';
import { Goal } from '@app/utils/goal';
import { Product } from '@app/utils/products';

export default function Dashboard() {
	const { currentUser } = useUser();
	const { color } = useOutletContext<{ color: string }>();
	const navigate = useNavigate();

	const [goal, setGoal] = useState<Goal | null>(null);
	const [balance, setBalance] = useState<number>(0);

	useEffect(() => {
		if (currentUser === null) {
			navigate('/auth/login');
			return;
		}

		(async () => {
			const lastGoal = await Goal.getLastGoal(currentUser.bank_account_id);
			if (!lastGoal) {
				navigate(`/goal/new?bank_account_id=${currentUser.bank_account_id}`);
				return;
			}
			setGoal(lastGoal);

			const balance = await Product.getProductCount(currentUser.bank_account_id, 'money');
			setBalance(balance);
		})();
	}, [currentUser, navigate]);

	if (!goal) return null;

	const userSpec = [
		{ name: 'номер банковского счета', value: currentUser?.bank_account_id.toString() ?? '' },
		{ name: 'полное имя', value: currentUser?.full_name ?? '' },
		{ name: 'логин', value: currentUser?.login ?? '' },
		{ name: 'день рождения', value: currentUser?.birthday ?? '' },
		{ name: 'бонус', value: currentUser?.bonus?.toString() ?? '' },
	];

	return (
		<Accordion defaultActiveKey="0">
			<Accordion.Item eventKey="0">
				<Accordion.Header>Профиль</Accordion.Header>
				<Accordion.Body>
					<div className="goal-section text-center border-bottom pb-3 mb-3">
						<p className="mb-1">
							<strong>Цель по доходу в день:</strong> <b>{goal.value}</b> Ψ
						</p>
						<ProgressBar
							now={goal.getProgressRate(balance)}
							label={`${goal.getProgressRate(balance)}%`}
							animated
							striped
							variant="success"
						/>
					</div>

					<div className="balance-blur text-center mb-3 rounded">
						<span>
							<strong>Баланс: {balance}</strong> Ψ
						</span>
					</div>

					<Table striped>
						<thead>
							<tr>
								<th colSpan={2}>Ваши данные:</th>
							</tr>
						</thead>
						<tbody>
							{userSpec.map((entry) => (
								<tr key={entry.name}>
									<th>{entry.name}</th>
									<td>{entry.value}</td>
								</tr>
							))}
						</tbody>
					</Table>

					<div className="d-grid">
						<a className={`${color} btn-lg`} href="/api/user/products">
							Ваши продукты
						</a>
					</div>
				</Accordion.Body>
			</Accordion.Item>

			<Accordion.Item eventKey="1">
				<Accordion.Header>Операции со счетом</Accordion.Header>
				<Accordion.Body className="d-grid gap-3">
					<a className={`${color} btn-lg`} href="/api/proposal/money">
						Перевод
					</a>
					<a className={`${color} btn-lg`} href="/api/proposal/bill">
						Выставить счет
					</a>
					<a className={`${color} btn-lg`} href="/api/proposal/unpaid">
						Неоплаченные счета
					</a>
					<a className={`${color} btn-lg`} href="/api/proposal/history">
						История транзакций
					</a>
				</Accordion.Body>
			</Accordion.Item>
		</Accordion>
	);
}
