import {
	GetLastGoalRequest,
	GoalResponse,
	CreateGoalRequest,
	CreateGoalResponse,
	Goal as GoalProto
} from '@app/codegen/goal';

import { util } from '@app/utils/wrappers';

export namespace GoalAPI {
	export function getProgressRate(goal: GoalProto, currentBalance: number): number {
		if (!goal.value || goal.value === 0) return 0;
		return Math.min(100, Math.floor((currentBalance / goal.value) * 100));
	}

	export async function getLastGoal(bank_account_id: number): Promise<GoalProto | null> {
		const req = GetLastGoalRequest.create({ bankAccountId: bank_account_id });

		const response = await util.wrapApiCall(() =>
			fetch('/api/goals/get_last', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/octet-stream',
				},
				credentials: 'include',
				body: GetLastGoalRequest.encode(req).finish(),
			})
		);

		if (response.status === 404) {
			return null;
		}

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = GoalResponse.decode(buffer);

		return parsed.goal ?? null;
	}

	export async function createGoal(bank_account_id: number, value: number | null): Promise<string> {
		const req = CreateGoalRequest.create({
			bankAccountId: bank_account_id,
			value: value ?? 0,
		});

		const response = await util.wrapApiCall(() =>
			fetch('/api/goals/create', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/octet-stream',
				},
				credentials: 'include',
				body: CreateGoalRequest.encode(req).finish(),
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = CreateGoalResponse.decode(buffer);

		return parsed.status;
	}
}
