import { BrowserRouter, Routes, Route } from 'react-router-dom';

import AuthLayout from '@app/layouts/auth';
import GreetingsLayout from '@app/layouts/main';

import { UserProvider } from '@app/contexts/user';

import HomePage from '@app/pages/home_page';
import LoginPage from '@app/pages/auth/login';
import PersonalPage from '@app/pages/accounts/personal';
import GoalPage from '@app/pages/auxiliary/new_goal';

function App() {
	return (
		<BrowserRouter>
			<UserProvider>
				<Routes>
					<Route element={<GreetingsLayout />}>
						<Route path="/" element={<HomePage />} />
						<Route path="/personal" element={<PersonalPage />} />
						<Route path="/goal/new" element={<GoalPage />} />
					</Route>

					<Route element={<AuthLayout />}>
						<Route path="/auth/login" element={<LoginPage />} />
					</Route>
				</Routes>
			</UserProvider>
		</BrowserRouter>
	);
}

export default App;
