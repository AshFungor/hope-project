import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Auth } from '../../utils/auth';
import { useUser } from '@app/contexts/user';

export default function LoginPage() {
	const [login, setLogin] = useState('');
	const [password, setPassword] = useState('');
	const [error, setError] = useState('');
	const navigate = useNavigate();
	const { refreshUser } = useUser();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		try {
			const response = await Auth.login(login, password);
			if (!response.ok) {
				setError('Введен неправильный логин или пароль');
			} else {
				await refreshUser(); // Обновление контекста пользователя
				navigate('/');
			}
		} catch (err) {
			console.error('Network or server error:', err);
			setError('Ошибка подключения к серверу');
		}
	};

	return (
		<main className="form-signin">
			<form onSubmit={handleSubmit}>
				<h1 className="h3 mb-3 fw-normal text-center">Пожалуйста, войдите</h1>

				{error && (
					<div className="alert alert-danger fade-in" role="alert">
						{error}
					</div>
				)}

				<div className="form-floating mb-3">
					<input
						type="text"
						className="form-control"
						id="floatingInput"
						placeholder="Login"
						value={login}
						onChange={(e) => setLogin(e.target.value)}
						required
					/>
					<label htmlFor="floatingInput">Логин</label>
				</div>

				<div className="form-floating mb-3">
					<input
						type="password"
						className="form-control"
						id="floatingPassword"
						placeholder="Password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						required
					/>
					<label htmlFor="floatingPassword">Пароль</label>
				</div>

				<button className="w-100 btn btn-lg btn-primary" type="submit">
					Войти
				</button>
			</form>
		</main>
	);
}
