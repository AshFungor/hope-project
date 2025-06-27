import { useEffect, useState } from 'react';
import { Accordion, Table } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';
import { GoalAPI } from '@app/types/goal';
import { ProductAPI } from '@app/types/product';

import BalanceSection from '@app/pages/shared/widgets/balance';
import GoalSection from '@app/pages/shared/widgets/goal';
import ProposalLinks from '@app/pages/shared/widgets/proposals';

import { Goal } from '@app/codegen/goal'

export default function PersonalPage() {
	const { currentUser, refreshUser } = useUser();
	const navigate = useNavigate();

	const [goal, setGoal] = useState<Goal | null>(null);
	const [balance, setBalance] = useState<number>(0);

	useEffect(() => {
		if (currentUser === null) {
			refreshUser();
			return;
		}

		(async () => {
			const lastGoal = await GoalAPI.getLastGoal(currentUser.bankAccountId);
			if (!lastGoal) {
				navigate(`/goal/new?bank_account_id=${currentUser.bankAccountId}`);
				return;
			}
			setGoal(lastGoal);

			const balance = await ProductAPI.count(currentUser.bankAccountId, 'надик');
			setBalance(balance);
		})();
	}, [currentUser, navigate]);

	const goToProducts = () => {
		navigate(`/products?bank_account_id=${currentUser?.bankAccountId}`);
	};

	if (!goal) return null;

	const userSpec = [
		{ name: 'номер банковского счета', value: currentUser?.bankAccountId.toString() ?? '' },
		{ name: 'полное имя', value: currentUser?.name ?? '' },
		{ name: 'логин', value: currentUser?.login ?? '' },
		{ name: 'день рождения', value: currentUser?.birthday ?? '' },
		{ name: 'бонус', value: currentUser?.bonus?.toString() ?? '' },
	];

	return (
		<Accordion defaultActiveKey="0">
			<Accordion.Item eventKey="0">
				<Accordion.Header>Профиль</Accordion.Header>
				<Accordion.Body>
					<GoalSection goal={goal} balance={balance} />
                    <div className="text-center mb-3 rounded blur" style={{ textAlign: 'center' }}>
					    <BalanceSection current={balance} />
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
						<button className="btn btn-outline-dark btn-lg mb-3" onClick={goToProducts}>
							Перейти к продуктам
						</button>
					</div>
				</Accordion.Body>
			</Accordion.Item>

			<Accordion.Item eventKey="1">
				<Accordion.Header>Операции со счетом</Accordion.Header>
				<Accordion.Body className="d-grid gap-3">
					<ProposalLinks accountId={currentUser?.bankAccountId}/>
				</Accordion.Body>
			</Accordion.Item>
		</Accordion>
	);
}
