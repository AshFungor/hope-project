import { Request } from '@app/codegen/app/protos/request';
import { Protobuf } from '@app/api/request';

import { User as UserType } from '@app/codegen/app/protos/types/user';

export class User implements UserType {
	constructor(
		public name: string,
		public lastName: string,
		public patronymic: string,
		public login: string,
		public sex: string,
		public bonus: number,
		public birthday: string,
		public bankAccountId: number,
		public prefectureName: string,
		public isAdmin: boolean
	) {}

	// was used before on personal page
	getFullname(): string {
		return `${this.name} ${this.lastName} ${this.patronymic}`;
	}
}

export namespace API {
	export namespace Session {
		export async function handle(request: Request) {
			if (request.login) {
				return Protobuf.send('/api/session/login', request, 'POST');
			}

			if (request.logout) {
				return Protobuf.send('/api/session/logout', request, 'POST');
			}

			throw new Error('Unsupported Session payload type');
		}
	}
}
