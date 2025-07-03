import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useUser } from '@app/contexts/user';
import { MessageAlert } from '@app/widgets/shared/alert';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { LoginRequest, LoginResponse_LoginStatus } from '@app/codegen/app/protos/session/login';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';

export default function LoginPage() {
	const [login, setLogin] = useState('');
	const [password, setPassword] = useState('');
	const [error, setMessage] = useState('');

	const navigate = useNavigate();
	const { refreshUser } = useUser();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setMessage('');

		try {
			const loginRequest = LoginRequest.create({ login, password });
			const response = await Hope.send(Request.create({ login: loginRequest }));

			if (response.login?.status !== LoginResponse_LoginStatus.OK) {
				setMessage('Введен неправильный логин или пароль');
			} else {
				await refreshUser();
				navigate('/');
			}
		} catch (err) {
			setMessage('Ошибка подключения к серверу');
		}
	};

	return (
		<Container maxWidth="xs">
			<Box
				component="form"
				onSubmit={handleSubmit}
				sx={{
					mt: 8,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
				}}
			>
				<Typography component="h1" variant="h5" sx={{ mb: 3 }}>
					Пожалуйста, войдите
				</Typography>

				<MessageAlert message={error} />

				<TextField
					margin="normal"
					required
					fullWidth
					id="login"
					label="Логин"
					name="login"
					autoComplete="username"
					autoFocus
					value={login}
					onChange={(e) => setLogin(e.target.value)}
				/>

				<TextField
					margin="normal"
					required
					fullWidth
					name="password"
					label="Пароль"
					type="password"
					id="password"
					autoComplete="current-password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
				/>

				<Button type="submit" fullWidth variant="contained" size="large" sx={{ mt: 3 }}>
					Войти
				</Button>
			</Box>
		</Container>
	);
}
