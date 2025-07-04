import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';

import { Hope } from '@app/api/api';

import BalanceSection from '@app/widgets/shared/balance';
import GoalSection from '@app/widgets/shared/goal';

import { Goal } from '@app/api/sub/goal';
import { GetLastGoalRequest } from '@app/codegen/app/protos/goal/last';
import { Request } from '@app/codegen/app/protos/request';
import { ProductCountsRequest } from '@app/codegen/app/protos/product/count';

import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import TableBody from '@mui/material/TableBody';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

export default function PersonalPage() {
	const { currentUser, refreshUser } = useUser();
	const navigate = useNavigate();

	const [goal, setGoal] = useState<Goal | null>(null);
	const [balance, setBalance] = useState<number>(0);

	useEffect(() => {
		if (currentUser === null) {
			refreshUser();
			navigate(-1);
			return;
		}

		(async () => {
			const lastGoalReq = GetLastGoalRequest.create({
				bankAccountId: currentUser.bankAccountId,
			});

			const lastGoalResponse = await Hope.send(Request.create({ lastGoal: lastGoalReq }));

			const lastGoal = lastGoalResponse.lastGoal?.goal ?? null;

			if (!lastGoal) {
				navigate('/personal/goal/new');
				return;
			}
			setGoal(new Goal(lastGoal.bankAccountId, lastGoal.value, lastGoal.currentProgress));

			const countReq = ProductCountsRequest.create({
				bankAccountId: currentUser.bankAccountId,
			});
			const countResponse = await Hope.send(Request.create({ productCounts: countReq }));

			const counts = countResponse?.productCounts?.products ?? null;
			if (counts === null) {
				throw Error('failed to fetch balance: could not complete request');
			}
			for (const count of counts) {
				if (count.product?.category === 'MONEY') {
					setBalance(count?.count ?? 0);
					return;
				}
			}
			setBalance(0);
		})();
	}, [currentUser, navigate]);

	const goToProducts = () => {
		navigate('/personal/products');
	};

	return (
		<Box>
			<Accordion defaultExpanded>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>Профиль</AccordionSummary>
				<AccordionDetails>
					<GoalSection goal={goal} />

					<Box
						className="blur"
						sx={{
							textAlign: 'center',
							mb: 3,
							p: 2,
							borderRadius: 1,
						}}
					>
						<BalanceSection current={balance} />
					</Box>

					<Table>
						<TableHead>
							<TableRow>
								<TableCell colSpan={2}>Ваши данные:</TableCell>
							</TableRow>
						</TableHead>
						<TableBody>
							<TableRow>
								<TableCell>номер банковского счета</TableCell>
								<TableCell>
									{currentUser?.bankAccountId?.toString() ?? ''}
								</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>имя</TableCell>
								<TableCell>{currentUser?.name ?? ''}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>логин</TableCell>
								<TableCell>{currentUser?.login ?? ''}</TableCell>
							</TableRow>
							<TableRow>
								<TableCell>бонус</TableCell>
								<TableCell>{currentUser?.bonus?.toString() ?? ''}</TableCell>
							</TableRow>
						</TableBody>
					</Table>

					<Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
						<Button variant="outlined" size="large" onClick={goToProducts}>
							Перейти к продуктам
						</Button>
						<Button
							variant="outlined"
							size="large"
							onClick={() => navigate('/personal/consumption/history')}
						>
							История потребления
						</Button>
					</Box>
				</AccordionDetails>
			</Accordion>

			<Accordion>
				<AccordionSummary expandIcon={<ExpandMoreIcon />}>
					Операции со счетом
				</AccordionSummary>
				<AccordionDetails>
					<Stack spacing={2}>
						<Button
							variant="outlined"
							size="large"
							onClick={() => navigate('/personal/proposal/money')}
						>
							Перевод
						</Button>
						<Button
							variant="outlined"
							size="large"
							onClick={() => navigate('/personal/proposal/product')}
						>
							Выставить счет
						</Button>
						<Button
							variant="outlined"
							size="large"
							onClick={() => navigate('/personal/proposal/unpaid')}
						>
							Неоплаченные счета
						</Button>
						<Button
							variant="outlined"
							size="large"
							onClick={() => navigate('/personal/proposal/history')}
						>
							История транзакций
						</Button>
					</Stack>
				</AccordionDetails>
			</Accordion>
		</Box>
	);
}
