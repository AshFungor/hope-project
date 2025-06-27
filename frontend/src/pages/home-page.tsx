import { useNavigate } from 'react-router-dom';

import { useUser } from '@app/contexts/user';


const HomePage = () => {
	const navigate = useNavigate();
	const { currentUser } = useUser();

	const go = (path: string) => navigate(path);

	return (
		<div className="container overflow-hidden">
			<div className="d-grid gap-2 d-mb-block mb-4">
				<button
					className="btn btn-outline-dark btn-lg mb-3"
					onClick={() => go('/personal')}
				>
					Личный кабинет
				</button>
				<button
					className="btn btn-outline-dark btn-lg mb-3"
					onClick={() => go('/company')}
				>
					Фирма
				</button>
				<button
					className="btn btn-outline-dark btn-lg mb-3"
					onClick={() => go('/prefecture')}
				>
					Префектура
				</button>
				<button
					className="btn btn-outline-dark btn-lg mb-3"
					onClick={() => go('/city_hall')}
				>
					Мэрия
				</button>
				{currentUser?.isAdmin && (
					<button
						className="btn btn-outline-dark btn-lg mb-3"
						onClick={() => go('/master')}
					>
						Мастер игры
					</button>
				)}
			</div>
		</div>
	);
};

export default HomePage;
