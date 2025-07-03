import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { CurrentPrefectureRequest } from '@app/codegen/app/protos/prefecture/current';
import { PartialUserRequest } from '@app/codegen/app/protos/user/partial';
import { GetLastGoalRequest } from '@app/codegen/app/protos/goal/last';
import { ProductCountsRequest } from '@app/codegen/app/protos/product/count';

import BalanceSection from '@app/widgets/shared/balance';
import GoalSection from '@app/widgets/shared/goal';
import { Goal } from '@app/api/sub/goal';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Button from '@mui/material/Button';

export default function PrefectureAccountPage() {
	const { currentUser } = useUser();
	const navigate = useNavigate();

	const [name, setName] = useState('');
	const [balance, setBalance] = useState(0);
	const [prefectName, setPrefectName] = useState('');
	const [prefectureBankAccount, setPrefectureBankAccount] = useState(0);
	const [ecoAssistantName, setEcoAssistantName] = useState('');
	const [socialAssistantName, setSocialAssistantName] = useState('');
	const [goal, setGoal] = useState<Goal | null>(null);

	const [isPrefect, setIsPrefect] = useState(false);
	const [isEcoAssistant, setIsEcoAssistant] = useState(false);

	useEffect(() => {
		if (!currentUser) return;

		(async () => {
			const prefReq: CurrentPrefectureRequest = {
				bankAccountId: currentUser.bankAccountId,
			};
			const prefResp = await Hope.sendTyped(
				Request.create({ currentPrefecture: prefReq }),
				'currentPrefecture'
			);

			const p = prefResp.prefecture;
			if (!p) return;

			setName(p.name ?? '—');

			const getUserName = async (accountId: number) => {
				const partialUser = PartialUserRequest.create({ bankAccountId: accountId });
				const resp = await Hope.send(Request.create({ partialUser: partialUser }));
				const nameString = (name: string, last_name: string) => `${name} ${last_name}`;
				if (!resp.partialUser) return '-';
				const user = resp.partialUser.user;
				return nameString(user?.name ?? '', user?.lastName ?? '');
			};

			const [prefect, eco, social] = await Promise.all([
				getUserName(p.prefectAccountId),
				getUserName(p.economicAssistantAccountId),
				getUserName(p.socialAssistantAccountId),
			]);

			setPrefectName(prefect);
			setEcoAssistantName(eco);
			setSocialAssistantName(social);
			setPrefectureBankAccount(p.bankAccountId);

			const userIsPrefect = currentUser.bankAccountId === p.prefectAccountId;
			const userIsEcoAssistant = currentUser.bankAccountId === p.economicAssistantAccountId;

			setIsPrefect(userIsPrefect);
			setIsEcoAssistant(userIsEcoAssistant);

			const countReq: ProductCountsRequest = { bankAccountId: p.bankAccountId };
			const countResp = await Hope.sendTyped(
				Request.create({ productCounts: countReq }),
				'productCounts'
			);

			const money = countResp.products?.find((p) => p.product?.category === 'MONEY');
			setBalance(money?.count ?? 0);

			const goalReq: GetLastGoalRequest = { bankAccountId: p.bankAccountId };
			const goalResp = await Hope.sendTyped(
				Request.create({ lastGoal: goalReq }),
				'lastGoal'
			);
			const g = goalResp.goal;

			if (g) {
				setGoal(new Goal(Number(g.bankAccountId), g.value));
			} else {
				if (userIsPrefect) {
					navigate(`/prefecture/${p.bankAccountId}/goal/new`);
					return;
				}
				setGoal(null);
			}
		})();
	}, [currentUser, navigate]);

	const handleNavigate = (path: string) => {
		navigate(path);
	};

	return (
		<Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
			<Box sx={{ mb: 3, textAlign: 'center', borderBottom: 1, borderColor: 'divider' }}>
				<Typography variant="h5" fontWeight="bold">
					Префектура {name}
				</Typography>
			</Box>

			<BalanceSection current={balance} />
			<GoalSection goal={goal} balance={balance} />

			<Table sx={{ mt: 3 }}>
				<TableHead>
					<TableRow>
						<TableCell colSpan={2}>Данные о префектуре:</TableCell>
					</TableRow>
				</TableHead>
				<TableBody>
					<TableRow>
						<TableCell>Префект</TableCell>
						<TableCell>{prefectName}</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>Заместитель по экономике</TableCell>
						<TableCell>{ecoAssistantName}</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>Заместитель по соц. политике</TableCell>
						<TableCell>{socialAssistantName}</TableCell>
					</TableRow>
					<TableRow>
						<TableCell>Номер банковского счета</TableCell>
						<TableCell>{prefectureBankAccount}</TableCell>
					</TableRow>
				</TableBody>
			</Table>

			{isEcoAssistant && (
				<Stack spacing={2} sx={{ mt: 4 }}>
					<Button
						variant="outlined"
						color="primary"
						size="large"
						onClick={() =>
							handleNavigate(`/prefecture/${prefectureBankAccount}/proposal/money`)
						}
					>
						Перевод
					</Button>

					<Button
						variant="outlined"
						color="primary"
						size="large"
						onClick={() =>
							handleNavigate(`/prefecture/${prefectureBankAccount}/proposal/history`)
						}
					>
						Просмотреть транзакции
					</Button>
				</Stack>
			)}
		</Box>
	);
}
