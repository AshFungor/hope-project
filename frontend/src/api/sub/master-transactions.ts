// @app/api/sub/master.ts

import { Request } from '@app/codegen/app/protos/request';
import { Protobuf } from '@app/api/request';

export namespace API {
	export namespace Master {
		export async function handle(request: Request) {
			if (request.masterRemoveMoney) {
				return Protobuf.send('/api/transaction/master/remove_money', request, 'POST');
			}

			if (request.masterAddMoney) {
				return Protobuf.send('/api/transaction/master/add_money', request, 'POST');
			}

			if (request.masterAddProduct) {
				return Protobuf.send('/api/transaction/master/add_product', request, 'POST');
			}

			if (request.masterRemoveProduct) {
				return Protobuf.send('/api/transaction/master/remove_product', request, 'POST');
			}

			throw new Error('Unsupported Master request type');
		}
	}
}
