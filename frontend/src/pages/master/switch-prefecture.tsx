import React, { useState, useEffect } from "react";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";

interface Prefecture {
    id: number;
    name: string;
}

const SwitchPrefectureForm: React.FC = () => {
    const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
    const [bankAccountId, setBankAccountId] = useState("");
    const [prefectureId, setPrefectureId] = useState("");
    const [message, setMessage] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            try {
                const response = await Hope.send(
                    Request.create({ allPrefectures: {} })
                );
                const data = response.allPrefectures?.prefectures ?? [];
                setPrefectures(
                    data.map((p, index) => ({
                        id: Number(p.bankAccountId),
                        name: p.name || `Префектура ${index + 1}`,
                    }))
                );
            } catch (err) {
                console.error("failed to query prefectures:", err);
            }
        })();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const accountId = parseInt(bankAccountId, 10);
        const prefId = parseInt(prefectureId, 10);

        if (isNaN(accountId) || isNaN(prefId)) {
            setMessage("Введите корректные значения.");
            return;
        }

        const req = Request.create({
            updatePrefectureLink: {
                bankAccountId: accountId,
                prefectureId: prefId,
            },
        });

        const response = await Hope.send(req);

        if (response.updatePrefectureLink?.success) {
            setMessage(`Привязка счета ${accountId} к префектуре ${prefId} выполнена.`);
        } else {
            setMessage("Не удалось выполнить привязку. Проверьте данные.");
        }

        setBankAccountId("");
        setPrefectureId("");
    };

    return (
        <form className="switch-prefecture-form" onSubmit={handleSubmit}>
            {message && (
                <div className="alert alert-success fade-in mb-4" role="alert">
                    {message}
                </div>
            )}

            <div className="mb-3">
                <label className="form-label">Номер банковского счета</label>
                <input
                    type="number"
                    className="form-control text-center"
                    value={bankAccountId}
                    onChange={(e) => setBankAccountId(e.target.value)}
                    placeholder="Введите номер счета"
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Префектура</label>
                <select
                    className="form-select"
                    value={prefectureId}
                    onChange={(e) => setPrefectureId(e.target.value)}
                >
                    <option value="">Выберите префектуру</option>
                    {prefectures.map((p) => (
                        <option key={p.id} value={p.id}>
                            {p.name}
                        </option>
                    ))}
                </select>
            </div>

            <div className="d-grid gap-2 mb-4">
                <button type="submit" className="btn btn-success">
                    Сохранить
                </button>
            </div>
        </form>
    );
};

export default SwitchPrefectureForm;
