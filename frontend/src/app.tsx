import { BrowserRouter, Routes, Route } from 'react-router-dom';

import AuthLayout from '@app/layouts/auth';
import MainLayout from '@app/layouts/main';

import { UserProvider } from '@app/contexts/user';
import { EffectiveIdProvider } from "@app/contexts/abstract/current-bank-account"

import HomePage from '@app/pages/home';
import LoginPage from '@app/pages/login';
import PersonalPage from '@app/pages/accounts/personal';
import GoalPage from '@app/pages/shared/new-goal';
import ProductsPage from '@app/pages/shared/products/available-products';
import TransactionDecisionPage from '@app/pages/shared/transactions/unpaid'
import TransactionHistory from '@app/pages/shared/transactions/history'
import MoneyTransferForm from '@app/pages/shared/transactions/transaction'
import NewTransactionForm from '@app/pages/shared/transactions/proposal'
import MasterHomePage from "@app/pages/master/master";
import CityHallPage from "@app/pages/accounts/city-hall";
import NewProductForm from "@app/pages/master/add-product";
import SwitchPrefectureForm from "@app/pages/master/switch-prefecture";
import MasterActionsPage from "@app/pages/master/transactions";
import CreateCompanyForm from "@app/pages/master/create-company";

function App() {
	const personal = (
		<UserProvider>
			<Route path="/personal/index" element={<PersonalPage />} />
			<Route path="/personal/products" element={<ProductsPage />} />
			<Route path="/personal/goal/new" element={<GoalPage />} />
			<Route path="/personal/proposal/history" element={<TransactionHistory />} />
			<Route path="/personal/proposal/unpaid" element={<TransactionDecisionPage />} />
			<Route path="/personal/proposal/money" element={<MoneyTransferForm />} />
			<Route path="/personal/proposal/product" element={<NewTransactionForm />} />
		</UserProvider>
	)

	return (
		<BrowserRouter>
			<UserProvider>
				<Routes>
					<Route element={<MainLayout />}>
						{personal}
						<Route path="/" element={<HomePage />} />
						
						<Route path="/products" element={<ProductsPage />} />

						<Route path="/master" element={<MasterHomePage />} />
                		<Route path="/city_hall" element={<CityHallPage />} />
						
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
