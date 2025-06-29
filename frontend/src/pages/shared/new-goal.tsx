import React, { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";

import BalanceSection from "@app/widgets/shared/balance";
import { Goal } from "@app/codegen/app/protos/types/goal";
import { CreateGoalRequest } from "@app/codegen/app/protos/goal/create";

import { PageMode } from "@app/types";
import { useUser } from "@app/contexts/user";

interface GoalFormPageProps {
    mode: PageMode;
}

export default function GoalFormPage({ mode }: GoalFormPageProps) {
    const params = useParams();
    const { bankAccountId } = useUser();
    const navigate = useNavigate();
    const location = useLocation();

    const effectiveAccountId =
        mode === PageMode.Company
            ? Number(params.companyId)
            : bankAccountId;

    const paramsSearch = new URLSearchParams(location.search);
    const current = Number(paramsSearch.get("current"));

    const [value, setValue] = useState<number | undefined>();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!effectiveAccountId) {
            throw new Error("No effective account ID found");
        }

        const goal = Goal.create({
            bankAccountId: effectiveAccountId,
            value: value,
        });
        const createGoalReq = CreateGoalRequest.create({ goal });

        await Hope.send(Request.create({ createGoal: createGoalReq }));
        navigate(-1);
    };

    const handleSkip = async () => {
        if (!effectiveAccountId) {
            throw new Error("No effective account ID found");
        }

        const goal = Goal.create({
            bankAccountId: effectiveAccountId,
            value: 0,
        });
        const createGoalReq = CreateGoalRequest.create({ goal });

        await Hope.send(Request.create({ createGoal: createGoalReq }));
        navigate(-1);
    };

    if (!effectiveAccountId) {
        return <p>Не удалось определить счёт</p>;
    }

    return (
        <form onSubmit={handleSubmit}>
            <div className="mb-4">
                <p className="mb-1">
                    <strong>Ваш счёт:</strong> {effectiveAccountId}
                </p>
            </div>

            <BalanceSection current={current} />

            <div className="form-group mb-4">
                <input
                    className="form-control text-center"
                    type="number"
                    name="value"
                    min="1"
                    placeholder="Введите цель на сегодня (в надиках)"
                    value={value ?? ""}
                    onChange={(e) => setValue(Number(e.target.value))}
                />
            </div>

            <div className="d-grid gap-2 d-mb-block mb-4">
                <button type="submit" className="btn btn-success btn-sm mb-3">
                    Установить цель
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={handleSkip}>
                    Пропустить
                </button>
            </div>
        </form>
    );
}
