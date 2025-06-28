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
import NewTransactionForm from '@app/pages/shared/views/transactions/proposal'
import MasterHomePage from "@app/pages/master/master";
import CityHallPage from "@app/pages/accounts/city-hall";
import NewProductForm from "@app/pages/master/add-product";
import SwitchPrefectureForm from "@app/pages/master/switch-prefecture";
import MasterActionsPage from "@app/pages/master/transactions";
import CreateCompanyForm from "@app/pages/master/create-company";

function App() {
	return (
		<BrowserRouter>
			<UserProvider>
				<Routes>
					<Route element={<MainLayout />}>
						<Route path="/" element={<HomePage />} />
						<Route path="/personal" element={<PersonalPage />} />
						<Route path="/master" element={<MasterHomePage />} />
                		<Route path="/city_hall" element={<CityHallPage />} />
						<Route path="/goal/new" element={<GoalPage />} />
						<Route path="/products" element={<ProductsPage />} />
						<Route path="/proposal/history/:accountId" element={<TransactionHistory />} />
						<Route path="/proposal/unpaid/:accountId" element={<TransactionDecisionPage />} />
						<Route path="/proposal/money/:accountId" element={<MoneyTransferForm />} />
						<Route path="/proposal/product/:accountId" element={<NewTransactionForm />} />
						<Route path="/master/product/create" element={<NewProductForm />} />
						<Route path="/master/resources" element={<MasterActionsPage />} />
						<Route path="/master/prefecture/update" element={<SwitchPrefectureForm/>} />
						<Route path="/master/company/create" element={<CreateCompanyForm />} />
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
