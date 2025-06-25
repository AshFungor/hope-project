import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';

import { getColorForBigButton } from '@app/utils/color';
import { Auth } from '@app/utils/auth';

import Header from '@app/layouts/base/header';
import Footer from '@app/layouts/base/footer';

export default function MainLayout() {
	const [color, setColor] = useState('btn btn-outline-dark');

	useEffect(() => {
		Auth.fetchCurrentUser()
			.then((data) => setColor(getColorForBigButton(data?.prefecture_name)))
			.catch(() => setColor(getColorForBigButton(null)));
	}, []);

	return (
		<div className="container overflow-hidden d-flex flex-column min-vh-100">
			<Header showLogout />
			<main className="flex-grow-1 my-4">
				<Outlet context={{ color }} />
			</main>
			<Footer />
		</div>
	);
}
