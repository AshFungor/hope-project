import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { API as GoalAPI } from "@app/api/sub/goal";
import { Goal } from "@app/codegen/app/protos/types/goal";

interface Roles {
    economic_assistant?: boolean;
    social_assistant?: boolean;
}

// interface CityHallPageProps {
//     bankAccount: number;
//     mayor?: string;
//     economic_assistant?: string;
//     social_assistant?: string;
// }

interface CityHallPageProps {
}

const CityHallPage: React.FC<CityHallPageProps> = ({
    // bankAccount,
    // mayor,
    // economic_assistant,
    // social_assistant,
}) => {
    const navigate = useNavigate();

    const [balance, setBalance] = useState<number>(0);
    const [goal, setGoal] = useState<Goal | null>(null);
    const [roles, setRoles] = useState<Roles>({});

    // useEffect(() => {
    //     // Example: roles may come from the same backend or context
    //     setRoles({
    //         economic_assistant: !!economic_assistant,
    //         social_assistant: !!social_assistant,
    //     });

    //     // Fetch balance, same as PersonalPage pattern
    //     (async () => {
    //         // Dummy: Replace with real `ProductAPI.count` or balance source.
    //         const dummyBalance = 750; // Replace with real fetch.
    //         setBalance(dummyBalance);

    //         // Load goal
    //         const goalResponse = await Hope.send(Request.create({ lastGoal: { bankAccountId: bankAccount } }));
    //         const lastGoal = goalResponse.lastGoal?.goal ?? null;

    //         setGoal(lastGoal);

    //         // If mayor exists but no goal → redirect to create goal page.
    //         if (mayor && !lastGoal) {
    //             navigate(`/goal/new?bank_account_id=${bankAccount}`);
    //         }
    //     })();
    // }, [bankAccount, mayor, navigate]);

    return (
        <div className="container my-4">
            <div className="text-center mb-3">
                <h3>
                    <strong>Мэрия &quot;Надежды&quot;</strong>
                </h3>
            </div>

            <div className="text-center mb-3 rounded blur position-relative">
                <style>
                    {`
                    .blur:before {
                        content: "";
                        position: absolute;
                        top: 0; left: 0; right: 0; bottom: 0;
                        background: linear-gradient(
                            0deg,
                            rgba(101,195,228,0.66) ${100 - balance / 10}%,
                            rgba(251,171,0,0.6) ${balance / 10}%
                        );
                        filter: blur(16px);
                        z-index: 0;
                    }
                    .blur span {
                        position: relative;
                        z-index: 1;
                    }
                    `}
                </style>
                <span>
                    <strong>Баланс: {balance}</strong> Ψ
                </span>
            </div>

            <table className="table table-striped">
                <thead>
                    <tr>
                        <th colSpan={2}>Данные о городе:</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <th>Номер банковского счета:</th>
                        {/* <td>{bankAccount}</td> */}
                    </tr>
                    <tr>
                        <th>Мэр:</th>
                        {/* <td>{mayor || "У мэрии пока нет мэра"}</td> */}
                    </tr>
                    <tr>
                        <th>Министр экономики:</th>
                        {/* <td>{economic_assistant || "У мэрии пока нет министра экономики"}</td> */}
                    </tr>
                    <tr>
                        <th>Министр социальной политики:</th>
                        {/* <td>{social_assistant || "У мэрии пока нет министра социальной политики"}</td> */}
                    </tr>
                </tbody>
            </table>

            {goal ? (
                <div className="text-start mb-5">
                    <p className="mb-1">
                        <strong>Цель по доходу в день:</strong>{" "}
                        <b>{goal.value}</b> Ψ
                    </p>
                    <div className="progress">
                        <div
                            className="bg-success progress-bar progress-bar-striped progress-bar-animated"
                            role="progressbar"
                            aria-valuenow={goal.value}
                            aria-valuemin={0}
                            aria-valuemax={100}
                            style={{ width: `${goal.value}%` }}
                        >
                            {goal.value}%
                        </div>
                    </div>
                </div>
            ) : (
                <div className="text-start mb-5">
                    <p className="mb-1">
                        <strong>Цель по доходу в день:</strong>{" "}
                        <b>не установлена</b> Ψ
                    </p>
                </div>
            )}

            {(roles.economic_assistant || roles.social_assistant) && (
                <div className="d-grid gap-2 mb-4">
                    <form action="/proposal/new_money_transaction" method="GET">
                        {/* <input type="hidden" name="account" value={bankAccount} /> */}
                        <button
                            className="btn btn-outline-dark btn-lg mb-3 w-100"
                            type="submit"
                        >
                            Перевод средств
                        </button>
                    </form>

                    <form action="/proposal/view_history" method="GET">
                        {/* <input type="hidden" name="account" value={bankAccount} /> */}
                        <button
                            className="btn btn-outline-dark btn-lg mb-3 w-100"
                            type="submit"
                        >
                            История транзакций
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default CityHallPage;
