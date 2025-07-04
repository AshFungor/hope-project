import { BrowserRouter, Routes, Route } from 'react-router-dom';

import AuthLayout from '@app/layouts/auth';

import { UserProvider } from '@app/contexts/user';
import { ThemeProvider } from '@app/contexts/theme';
import { PageMode } from '@app/types';

import HomePage from '@app/pages/home';
import LoginPage from '@app/pages/login';

import PersonalPage from '@app/pages/accounts/personal/personal';
import GoalPage from '@app/pages/shared/new-goal';
import ProductsPage from '@app/pages/shared/products/available-products';
import TransactionDecisionPage from '@app/pages/shared/transactions/unpaid';
import TransactionHistory from '@app/pages/shared/transactions/history';
import MoneyTransferForm from '@app/pages/shared/transactions/transaction';
import NewTransactionForm from '@app/pages/shared/transactions/proposal';
import ConsumptionHistoryPage from '@app/pages/accounts/personal/consumption-history'

import MasterHomePage from '@app/pages/master/master';
import CityHallPage from '@app/pages/accounts/city-hall';
import NewProductForm from '@app/pages/master/add-product';
import SwitchPrefectureForm from '@app/pages/master/switch-prefecture';
import MasterActionsPage from '@app/pages/master/transactions';
import MasterChangeCEOPage from './pages/master/change-ceo';
import CreateCompanyForm from '@app/pages/master/create-company';
import AllProductsPage from '@app/pages/master/all-products';

import CompanyListPage from '@app/pages/accounts/company/navigation';
import CompanyAccountPage from '@app/pages/accounts/company/company';
import CompanyEmployeesPage from '@app/pages/accounts/company/employees';
import CompanyEmployPage from '@app/pages/accounts/company/employ';

import PrefectureAccountPage from '@app/pages/accounts/prefecture';

import ViewConsumersPage from '@app/pages/master/view-consumers';

import MainLayout from './layouts/main';

import { EmployeeRole } from './codegen/app/protos/types/company';

function App() {
	return (
		<ThemeProvider>
			<BrowserRouter>
				<UserProvider>
					<Routes>
						<Route element={<MainLayout />}>
							<Route path="/personal/index" element={<PersonalPage />} />
							<Route
								path="/personal/products"
								element={<ProductsPage mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/goal/new"
								element={<GoalPage mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/proposal/history"
								element={<TransactionHistory mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/proposal/unpaid"
								element={<TransactionDecisionPage mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/proposal/money"
								element={<MoneyTransferForm mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/proposal/product"
								element={<NewTransactionForm mode={PageMode.Personal} />}
							/>
							<Route
								path="/personal/consumption/history"
								element={<ConsumptionHistoryPage />}
							/>

							<Route path="/companies" element={<CompanyListPage />} />
							<Route path="/company/:companyId" element={<CompanyAccountPage />} />
							<Route
								path="/company/:companyId/products"
								element={<ProductsPage mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:orgId/goal/new"
								element={<GoalPage mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:orgId/proposal/history"
								element={<TransactionHistory mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:orgId/proposal/unpaid"
								element={<TransactionDecisionPage mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:orgId/proposal/money"
								element={<MoneyTransferForm mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:orgId/proposal/product"
								element={<NewTransactionForm mode={PageMode.Org} />}
							/>
							<Route
								path="/company/:companyId/workers"
								element={<CompanyEmployeesPage />}
							/>
							<Route
								path="/company/:companyId/employees"
								element={<CompanyEmployeesPage />}
							/>
							<Route
								path="/company/:companyId/ceo/employ"
								element={
									<CompanyEmployPage
										permittedRoles={[
											EmployeeRole.CFO,
											EmployeeRole.MARKETING_MANAGER,
											EmployeeRole.PRODUCTION_MANAGER,
										]}
									/>
								}
							/>
							<Route
								path="/company/:companyId/production/employ"
								element={
									<CompanyEmployPage permittedRoles={[EmployeeRole.EMPLOYEE]} />
								}
							/>

							<Route path="/" element={<HomePage />} />

							<Route path="/prefecture/index" element={<PrefectureAccountPage />} />
							<Route
								path="/prefecture/:orgId/goal/new"
								element={<GoalPage mode={PageMode.Org} />}
							/>
							<Route
								path="/prefecture/:orgId/proposal/history"
								element={<TransactionHistory mode={PageMode.Org} />}
							/>
							<Route
								path="/prefecture/:orgId/proposal/money"
								element={<MoneyTransferForm mode={PageMode.Org} />}
							/>

							<Route path="/city_hall/index" element={<CityHallPage />} />
							<Route
								path="/city_hall/:orgId/goal/new"
								element={<GoalPage mode={PageMode.Org} />}
							/>
							<Route
								path="/city_hall/:orgId/proposal/history"
								element={<TransactionHistory mode={PageMode.Org} />}
							/>
							<Route
								path="/city_hall/:orgId/proposal/money"
								element={<MoneyTransferForm mode={PageMode.Org} />}
							/>

							<Route path="/master/index" element={<MasterHomePage />} />
							<Route path="/master/product/all" element={<AllProductsPage />} />
							<Route path="/master/product/create" element={<NewProductForm />} />
							<Route path="/master/resources" element={<MasterActionsPage />} />
							<Route
								path="/master/prefecture/update"
								element={<SwitchPrefectureForm />}
							/>
							<Route path="/master/company/create" element={<CreateCompanyForm />} />
							<Route
								path="/master/company/change-ceo"
								element={<MasterChangeCEOPage />}
							/>
							<Route
								path="/master/company/view-consumers"
								element={<ViewConsumersPage />}
							/>
						</Route>

						<Route element={<AuthLayout />}>
							<Route path="/auth/login" element={<LoginPage />} />
						</Route>
					</Routes>
				</UserProvider>
			</BrowserRouter>
		</ThemeProvider>
	);
}

export default App;
