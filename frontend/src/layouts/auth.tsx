import { Outlet } from 'react-router-dom';

import Header from '@app/layouts/base/header';
import Footer from '@app/layouts/base/footer';

import Box from '@mui/material/Box';
import Container from '@mui/material/Container';

export default function AuthLayout() {
	return (
		<Box
			sx={{
				display: 'flex',
				flexDirection: 'column',
				minHeight: '100vh',
				overflow: 'hidden',
			}}
		>
			<Header />
			<Container component="main" sx={{ flexGrow: 1, my: 4 }}>
				<Outlet />
			</Container>
			<Footer />
		</Box>
	);
}
