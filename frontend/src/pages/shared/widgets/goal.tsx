import { Goal } from '@app/api/sub/goal';
import { ProgressBar } from 'react-bootstrap';

interface GoalSelectionProperties {
	goal: Goal | null;
	balance: number;
}

export default function GoalSection({ goal, balance }: GoalSelectionProperties) {
	if (!goal || goal.value === null) {
		return (
			<div className="goal-section text-center border-bottom pb-3 mb-3">
				<p className="mb-0 text-muted">Цель не задана</p>
			</div>
		);
	}

	const progress = goal.getRate(balance);
	return (
		<div className="goal-section text-center border-bottom pb-3 mb-3">
			<p className="mb-1">
				<strong>Цель по доходу в день:</strong> <b>{goal.value}</b> Ψ
			</p>
			<ProgressBar now={progress} label={`${progress}%`} animated striped variant="success" />
		</div>
	);
}
