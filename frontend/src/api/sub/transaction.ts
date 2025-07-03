import { Request } from '@app/codegen/app/protos/request';
import { Protobuf } from '@app/api/request';

import {
	Transaction_Status,
	Transaction as TransactionType,
} from '@app/codegen/app/protos/types/transaction';

export class Transaction implements TransactionType {
	constructor(
		public sellerBankAccountId: number,
		public customerBankAccountId: number,
		public product: string,
		public count: number,
		public amount: number,
		public status: Transaction_Status,
		public transactionId: number,
		public createdAt: string,
		public updatedAt: string,
		public side: string,
		public isMoney: boolean
	) {}

	stringStatus(): string {
		switch (this.status) {
			case Transaction_Status.ACCEPTED:
				return 'подтверждено';
			case Transaction_Status.REJECTED:
				return 'отклонено';
			case Transaction_Status.CREATED:
				return 'создано';
			default:
				return '';
		}
	}
}

export namespace API {
	export namespace Transaction {
		export async function handle(request: Request) {
			if (request.createProductTransaction) {
				return Protobuf.send('/api/transaction/product/create', request, 'POST');
			}

			if (request.createMoneyTransaction) {
				return Protobuf.send('/api/transaction/money/create', request, 'POST');
			}

			if (request.decideOnTransaction) {
				return Protobuf.send('/api/transaction/decide', request, 'POST');
			}

			if (request.viewTransactionHistory) {
				return Protobuf.send('/api/transaction/history', request, 'POST');
			}

			if (request.currentTransactions) {
				return Protobuf.send('/api/transaction/current', request, 'POST');
			}

			throw new Error('Unsupported Transaction payload type');
		}
	}
}
