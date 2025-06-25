export class CurrentUser {
	constructor(
		public id: number,
		public bank_account_id: number,
		public city_name: string | null,
		public name: string,
		public last_name: string,
		public patronymic: string,
		public login: string,
		public sex: string,
		public bonus: number,
		public birthday: string,
		public is_admin: boolean,
		public prefecture_name: string | null
	) {}

	get full_name(): string {
		return `${this.last_name} ${this.name} ${this.patronymic}`;
	}

	static fromJson(json: any): CurrentUser {
		return new CurrentUser(
			json.id,
			json.bank_account_id,
			json.city_name,
			json.name,
			json.last_name,
			json.patronymic,
			json.login,
			json.sex,
			json.bonus,
			json.birthday,
			json.is_admin,
			json.prefecture_name
		);
	}
}
