import { CurrentUser } from '@app/types/user';
import { StatusCodes } from 'http-status-codes';

export class Auth {
	static async login(login: string, password: string): Promise<Response> {
		return fetch('/api/login', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
			body: JSON.stringify({ login, password }),
		});
	}

	static async logout(): Promise<Response> {
		return fetch('/api/logout', {
			method: 'POST',
			credentials: 'include',
		});
	}

	static async fetchCurrentUser(): Promise<CurrentUser | null> {
		const response = await fetch('/api/current_user', {
			credentials: 'include',
		});

		switch (response.status) {
			case StatusCodes.UNAUTHORIZED:
				console.log(
					'current user is non-authorized, context-aware decorations are not available'
				);
				return null;

			case StatusCodes.OK:
                let json = await response.json();
				return CurrentUser.fromJson(json);

			default:
				throw new Error('Failed to fetch user');
		}
	}
}
