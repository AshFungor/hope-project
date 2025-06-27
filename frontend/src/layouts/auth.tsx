import { Outlet } from 'react-router-dom';

import Header from '@app/layouts/base/header';
import Footer from '@app/layouts/base/footer';

export default function AuthLayout() {
	return (
		<div className="container overflow-hidden d-flex flex-column min-vh-100">
			<Header />
			<main className="flex-grow-1 my-4">
				<Outlet />
			</main>
			<Footer />
		</div>
	);
}
