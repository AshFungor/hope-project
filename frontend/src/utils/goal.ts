export class Goal {
	constructor(
		public bank_account_id: number,
		public created_at: string | null,
		public value: number | null
	) {}

	static async getLastGoal(bank_account_id: number): Promise<Goal | null> {
		const params = new URLSearchParams({ bank_account_id: bank_account_id.toString() });
		const response = await fetch(`/api/goals/get_last?${params.toString()}`, {
			credentials: 'include',
		});

		if (response.status === 404) {
			return null;
		}

		if (!response.ok) {
			throw new Error(`Failed to fetch goal: ${await response.text()}`);
		}

		const data = await response.json();
		return new Goal(data.bank_account_id, data.created_at, data.value);
	}

	static async createGoal(bank_account_id: number, value: number | null): Promise<void> {
		const response = await fetch('/api/goals/create', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
			body: JSON.stringify({
				bank_account_id: bank_account_id.toString(),
				value: value?.toString(),
			}),
		});

		if (!response.ok) {
			throw new Error(`Failed to create goal: ${await response.text()}`);
		}
	}

	getProgressRate(currentBalance: number): number {
		return Math.min(100, Math.floor((currentBalance / this.value!) * 100));
	}
}
