import { BrowserRouter, Routes, Route } from 'react-router-dom';

import AuthLayout from '@app/layouts/auth';
import MainLayout from '@app/layouts/main';

import { UserProvider } from '@app/contexts/user';

import HomePage from '@app/pages/home-page';
import LoginPage from '@app/pages/login';
import PersonalPage from '@app/pages/accounts/personal';
import GoalPage from '@app/pages/shared/views/new-goal';
import ProductsPage from '@app/pages/shared/views/available-products';
import TransactionDecisionPage from '@app/pages/shared/views/transactions/unpaid'
import TransactionHistory from '@app/pages/shared/views/transactions/history'
import MoneyTransferForm from '@app/pages/shared/views/transactions/transaction'

function App() {
	return (
		<BrowserRouter>
			<UserProvider>
				<Routes>
					<Route element={<MainLayout />}>
						<Route path="/" element={<HomePage />} />
						<Route path="/personal" element={<PersonalPage />} />
						<Route path="/goal/new" element={<GoalPage />} />
						<Route path="/products" element={<ProductsPage />} />
						<Route path="/proposal/history/:accountId" element={<TransactionHistory />} />
						<Route path="/proposal/unpaid/:accountId" element={<TransactionDecisionPage />} />
						<Route path="/proposal/money/:accountId" element={<MoneyTransferForm />} />
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
