import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import type { CurrentUser } from '@app/types/user';
import { getColorForBigButton } from '@app/utils/color';

const HomePage = () => {
	const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);
	const [colorForBigButton, setColorForBigButton] = useState<string>(getColorForBigButton(null));

	const navigate = useNavigate();

	useEffect(() => {
		fetch('/api/current_user')
			.then((res) => res.json())
			.then((data: CurrentUser) => {
				setCurrentUser(data);
				setColorForBigButton(getColorForBigButton(data.prefecture_name));
			})
			.catch(() => {
				setColorForBigButton(getColorForBigButton(null));
			});
	}, []);

	const go = (path: string) => navigate(path);

	return (
		<div className="container overflow-hidden">
			<div className="d-grid gap-2 d-mb-block mb-4">
				<button
					className={`${colorForBigButton} btn-lg mb-3`}
					onClick={() => go('/personal')}
				>
					Личный кабинет
				</button>
				<button
					className={`${colorForBigButton} btn-lg mb-3`}
					onClick={() => go('/company')}
				>
					Фирма
				</button>
				<button className={`${colorForBigButton} btn-lg mb-3`} onClick={() => go('/city')}>
					Город
				</button>
				<button
					className={`${colorForBigButton} btn-lg mb-3`}
					onClick={() => go('/prefecture')}
				>
					Префектура
				</button>
				<button
					className={`${colorForBigButton} btn-lg mb-3`}
					onClick={() => go('/city_hall')}
				>
					Мэрия
				</button>
				{currentUser?.is_admin && (
					<button
						className={`${colorForBigButton} btn-lg mb-3`}
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
