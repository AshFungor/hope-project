import { useEffect, useState } from "react";
import { Accordion, Table } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useUser } from "@app/contexts/user";

import { Hope } from "@app/api/api";

import BalanceSection from "@app/widgets/shared/balance";
import GoalSection from "@app/widgets/shared/goal";
import ProposalLinks from "@app/widgets/shared/proposals";

import { Goal } from "@app/api/sub/goal";
import { GetLastGoalRequest } from "@app/codegen/app/protos/goal/last";
import { Request } from "@app/codegen/app/protos/request";
import { ProductCountsRequest } from "@app/codegen/app/protos/products/count";

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

            const lastGoalResponse = await Hope.send(
                Request.create({ lastGoal: lastGoalReq })
            );

            const lastGoal = lastGoalResponse.lastGoal?.goal ?? null;

            if (!lastGoal) {
                navigate(`/goal/new?bank_account_id=${currentUser.bankAccountId}`);
                return;
            }
            setGoal(new Goal(lastGoal.bankAccountId, lastGoal.value));

            const countReq = ProductCountsRequest.create({
                bankAccountId: currentUser.bankAccountId
            });
            const countResponse = await Hope.send(
                Request.create({ productCounts: countReq })
            );

			// should move to separate context
			const counts = countResponse?.productCounts?.products ?? null
			if (counts === null) {
				throw Error("failed to fetch balance: could not complete request")
			}
			for (const count of counts) {
				if (count.product?.id == 1) {
					setBalance(count?.count ?? 0);
					return;
				}
			}
			setBalance(0);
        })();
    }, [currentUser, navigate]);

    const goToProducts = () => {
        navigate(`/products?bank_account_id=${currentUser?.bankAccountId}`);
    };

    return (
        <Accordion defaultActiveKey="0">
            <Accordion.Item eventKey="0">
                <Accordion.Header>Профиль</Accordion.Header>
                <Accordion.Body>
                    <GoalSection goal={goal} balance={balance} />
                    <div
                        className="text-center mb-3 rounded blur"
                        style={{ textAlign: "center" }}
                    >
                        <BalanceSection current={balance} />
                    </div>

                    <Table striped>
						<thead>
							<tr>
								<th colSpan={2}>Ваши данные:</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<th>номер банковского счета</th>
								<td>{currentUser?.bankAccountId?.toString() ?? ""}</td>
							</tr>
							<tr>
								<th>имя</th>
								<td>{currentUser?.name ?? ""}</td>
							</tr>
							<tr>
								<th>логин</th>
								<td>{currentUser?.login ?? ""}</td>
							</tr>
							<tr>
								<th>бонус</th>
								<td>{currentUser?.bonus?.toString() ?? ""}</td>
							</tr>
						</tbody>
					</Table>

                    <div className="d-grid">
                        <button
                            className="btn btn-outline-dark btn-lg mb-3"
                            onClick={goToProducts}
                        >
                            Перейти к продуктам
                        </button>
                    </div>
                </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="1">
                <Accordion.Header>Операции со счетом</Accordion.Header>
                <Accordion.Body className="d-grid gap-3">
                    <ProposalLinks accountId={currentUser?.bankAccountId} />
                </Accordion.Body>
            </Accordion.Item>
        </Accordion>
    );
}
