import { useNavigate } from 'react-router-dom';
import { Auth } from '@app/utils/auth';

export default function Header({ showLogout = false }: { showLogout?: boolean }) {
	const navigate = useNavigate();

	const handleLogout = () => {
		Auth.logout();
		navigate('/auth/login');
	};

	return (
		<header className="px-3 py-2 text-bg-dark border-bottom">
			<div className="container d-flex align-items-center justify-content-between">
				<a href="/" className="d-flex align-items-center text-white text-decoration-none">
					<img src="/images/logo.png" alt="" className="logo-small" />
				</a>
				{showLogout && (
					<button className="btn btn-outline-light ms-auto" onClick={handleLogout}>
						Выход
					</button>
				)}
			</div>
		</header>
	);
}
