import React, { useEffect, useState } from "react";
import { useUser } from "@app/contexts/user";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { CurrentPrefectureRequest, CurrentPrefectureResponse } from "@app/codegen/app/protos/prefecture/current";
import { GetLastGoalRequest, GetLastGoalResponse } from "@app/codegen/app/protos/goal/last";
import { ProductCountsRequest, ProductCountsResponse } from "@app/codegen/app/protos/product/count";

import BalanceSection from "@app/widgets/shared/balance";
import GoalSection from "@app/widgets/shared/goal";
import { Goal } from "@app/api/sub/goal";

export default function PrefectureAccountPage() {
    const { currentUser } = useUser();

    const [name, setName] = useState("");
    const [balance, setBalance] = useState(0);
    const [prefectName, setPrefectName] = useState("");
    const [ecoAssistant, setEcoAssistant] = useState("");
    const [socialAssistant, setSocialAssistant] = useState("");
    const [goal, setGoal] = useState<Goal | null>(null);

    useEffect(() => {
        if (!currentUser) return;

        (async () => {
            const prefReq: CurrentPrefectureRequest = { bankAccountId: currentUser.bankAccountId };
            const prefResp = await Hope.sendTyped(Request.create({ currentPrefecture: prefReq }), "currentPrefecture");

            const p = prefResp.prefecture;
            if (!p) return;

            setName(p.name ?? "—");
            setPrefectName("Имя Префекта");
            setEcoAssistant("Экономический заместитель");
            setSocialAssistant("Социальный заместитель");

            const countReq: ProductCountsRequest = { bankAccountId: currentUser.bankAccountId };
            const countResp = await Hope.sendTyped(Request.create({ productCounts: countReq }), "productCounts");
            const money = countResp.products?.find(p => p.product?.category === "MONEY");
            setBalance(money?.count ?? 0);

            const goalReq: GetLastGoalRequest = { bankAccountId: currentUser.bankAccountId };
            const goalResp = await Hope.sendTyped(Request.create({ lastGoal: goalReq }), "lastGoal");
            const g = goalResp.goal;
            setGoal(g ? new Goal(Number(g.bankAccountId), g.value) : null);
        })();
    }, [currentUser]);

    return (
        <div className="container mt-4">
            <div className="text-wrap text-center mb-3 rounded border-bottom" style={{ position: "relative" }}>
                <h3 style={{ position: "relative", zIndex: 1 }}>
                    <strong>Префектура {name}</strong>
                </h3>
            </div>

            <BalanceSection current={balance} />
            <GoalSection goal={goal} balance={balance} />

            <table className="table table-striped">
                <thead>
                    <tr>
                        <td colSpan={2}>Данные о префектуре:</td>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>Префект</th>
                        <td>{prefectName}</td>
                    </tr>
                    <tr>
                        <th>Заместитель по экономике</th>
                        <td>{ecoAssistant}</td>
                    </tr>
                    <tr>
                        <th>Заместитель по соц. политике</th>
                        <td>{socialAssistant}</td>
                    </tr>
                </tbody>
            </table>

            <div className="d-grid gap-2 mb-5">
                <button className="btn btn-outline-dark btn-lg mb-3">Перевод</button>
                <button className="btn btn-outline-dark btn-lg mb-3">Просмотреть транзакции</button>
            </div>
        </div>
    );
}
