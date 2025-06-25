export function getColorForBigButton(prefectureName: string | null | undefined): string {
	switch (prefectureName) {
		case 'Юг':
			return 'btn btn-outline-danger';
		case 'Восток':
			return 'btn btn-outline-warning';
		case 'Запад':
			return 'btn btn-outline-secondary';
		case 'Север':
			return 'btn btn-outline-primary';
		default:
			return 'btn btn-outline-dark';
	}
}

export function getColorForButton(prefectureName: string | null | undefined): string {
	switch (prefectureName) {
		case 'Юг':
			return 'btn btn-danger';
		case 'Восток':
			return 'btn btn-warning';
		case 'Запад':
			return 'btn btn-secondary';
		case 'Север':
			return 'btn btn-primary';
		default:
			return 'btn btn-dark';
	}
}
