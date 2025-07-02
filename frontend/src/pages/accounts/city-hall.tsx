import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { PartialUserRequest } from "@app/codegen/app/protos/user/partial";
import { GetLastGoalRequest } from "@app/codegen/app/protos/goal/last";
import { ProductCountsRequest } from "@app/codegen/app/protos/product/count";

import BalanceSection from "@app/widgets/shared/balance";
import GoalSection from "@app/widgets/shared/goal";
import { Goal } from "@app/api/sub/goal";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Button from "@mui/material/Button";
import { useUser } from "@app/contexts/user";
import { CityHallRequest } from "@app/codegen/app/protos/city_hall/current";

export default function CityHallPage() {
    const { currentUser } = useUser();
    const navigate = useNavigate();

    const [balance, setBalance] = useState<number>(0);
    const [goal, setGoal] = useState<Goal | null>(null);

    const [cityHallBankAccount, setCityHallBankAccount] = useState<number>(0);

    const [mayorName, setMayorName] = useState<string>("-");
    const [ecoAssistantName, setEcoAssistantName] = useState<string>("-");
    const [socialAssistantName, setSocialAssistantName] = useState<string>("-");

    const [isMayor, setIsMayor] = useState<boolean>(false);
    const [isEcoAssistant, setIsEcoAssistant] = useState<boolean>(false);
    const [isSocialAssistant, setIsSocialAssistant] = useState<boolean>(false);

    useEffect(() => {
        if (!currentUser) return;

        (async () => {
            const cityHallReq: CityHallRequest = {
                bankAccountId: currentUser.bankAccountId
            };
            const cityHallResp = await Hope.send(
                Request.create({ cityHall: cityHallReq })
            );

            const cityHall = cityHallResp.cityHall?.cityHall;
            if (!cityHall) return;

            setCityHallBankAccount(cityHall.bankAccountId);

            const getUserName = async (accountId: number) => {
                const req = PartialUserRequest.create({ bankAccountId: accountId });
                const resp = await Hope.send(Request.create({ partialUser: req }));
                if (!resp.partialUser) return "-";
                const u = resp.partialUser.user;
                return `${u?.name ?? ""} ${u?.lastName ?? ""}`.trim();
            };

            const [mayor, eco, social] = await Promise.all([
                getUserName(cityHall.mayorAccountId),
                getUserName(cityHall.economicAssistantAccountId),
                getUserName(cityHall.socialAssistantAccountId)
            ]);

            setMayorName(mayor);
            setEcoAssistantName(eco);
            setSocialAssistantName(social);

            const userIsMayor = currentUser.bankAccountId === cityHall.mayorAccountId;
            const userIsEco = currentUser.bankAccountId === cityHall.economicAssistantAccountId;
            const userIsSocial = currentUser.bankAccountId === cityHall.socialAssistantAccountId;

            setIsMayor(userIsMayor);
            setIsEcoAssistant(userIsEco);
            setIsSocialAssistant(userIsSocial);

            const countReq: ProductCountsRequest = { bankAccountId: cityHall.bankAccountId };
            const countResp = await Hope.sendTyped(
                Request.create({ productCounts: countReq }),
                "productCounts"
            );
            const money = countResp.products?.find(p => p.product?.category === "MONEY");
            setBalance(money?.count ?? 0);

            const goalReq: GetLastGoalRequest = { bankAccountId: cityHall.bankAccountId };
            const goalResp = await Hope.sendTyped(Request.create({ lastGoal: goalReq }), "lastGoal");
            const g = goalResp.goal;

            if (g) {
                setGoal(new Goal(Number(g.bankAccountId), g.value));
            } else {
                if (userIsMayor) {
                    navigate(`/city_hall/${cityHall.bankAccountId}/goal/new?current=${money?.count ?? 0}`);
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
        <Box sx={{ maxWidth: 800, mx: "auto", mt: 4 }}>
            <Box sx={{ mb: 3, textAlign: "center", borderBottom: 1, borderColor: "divider" }}>
                <Typography variant="h5" fontWeight="bold">
                    Мэрия города
                </Typography>
            </Box>

            <BalanceSection current={balance} />
            <GoalSection goal={goal} balance={balance} />

            <Table sx={{ mt: 3 }}>
                <TableHead>
                    <TableRow>
                        <TableCell colSpan={2}>Данные о мэрии:</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    <TableRow>
                        <TableCell>Номер банковского счета</TableCell>
                        <TableCell>{cityHallBankAccount}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Мэр</TableCell>
                        <TableCell>{mayorName}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Министр экономики</TableCell>
                        <TableCell>{ecoAssistantName}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Министр социальной политики</TableCell>
                        <TableCell>{socialAssistantName}</TableCell>
                    </TableRow>
                    <TableRow>
                        <TableCell>Номер банковского счета</TableCell>
                        <TableCell>{cityHallBankAccount}</TableCell>
                    </TableRow>
                </TableBody>
            </Table>

            {(isEcoAssistant) && (
                <Stack spacing={2} sx={{ mt: 4 }}>
                    <Button
                        variant="outlined"
                        size="large"
                        onClick={() => handleNavigate(`/city_hall/${cityHallBankAccount}/proposal/money`)}
                    >
                        Перевод средств
                    </Button>

                    <Button
                        variant="outlined"
                        size="large"
                        onClick={() => handleNavigate(`/city_hall/${cityHallBankAccount}/proposal/history`)}
                    >
                        История транзакций
                    </Button>
                </Stack>
            )}
        </Box>
    );
}
