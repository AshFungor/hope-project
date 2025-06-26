import { util } from '@app/utils/wrappers';

export namespace TransactionAPI {
	export interface TransactionRecord {
		transaction_id: number;
		product: string;
		count: number;
		amount: number;
		status: string;
		updated_at: string;
		side: 'seller' | 'customer';
		second_side: number;
		is_money: boolean;
	}

	export async function createProductProposal(
		seller_account: number,
		customer_account: number,
		product: string,
		count: number,
		amount: number
	): Promise<Response> {
		return util.wrapApiCall(() =>
			fetch('/api/transaction/product/create', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					seller_account,
					customer_account,
					product,
					count,
					amount,
				}),
			})
		);
	}

	export async function createMoneyProposal(
		seller_account: number,
		customer_account: number,
		amount: number
	): Promise<Response> {
		return util.wrapApiCall(() =>
			fetch('/api/transaction/money/create', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					seller_account,
					customer_account,
					amount,
				}),
			})
		);
	}

	export async function getActiveProposals(account: number): Promise<Array<{
		transaction_id: number;
		product: string;
		count: number;
		amount: number;
		second_side: number;
	}>> {
		const response = await util.wrapApiCall(() =>
			fetch('/api/transaction/view/current', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({ account }),
			})
		);

		return JSON.parse(await response.text());
	}

	export async function getTransactionHistory(account: number): Promise<TransactionRecord[]> {
		const response = await util.wrapApiCall(() =>
			fetch('/api/transaction/view/history', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({ account }),
			})
		);

		return JSON.parse(await response.text());
	}

	export async function decideOnProposal(
		transaction_id: number,
		status: 'approved' | 'rejected'
	): Promise<Response> {
		return util.wrapApiCall(() =>
			fetch('/api/transaction/decide', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				credentials: 'include',
				body: JSON.stringify({
					account: transaction_id,
					status,
				}),
			})
		);
	}
}
