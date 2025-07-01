import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import {
    CreateCompanyRequest,
    CreateCompanyResponse,
    CreateCompanyResponse_Status,
    Founder,
} from "@app/codegen/app/protos/company/create";
import { AllPrefecturesRequest, AllPrefecturesResponse } from "@app/codegen/app/protos/prefecture/all";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

interface Prefecture {
    id: number;
    name: string;
}

export default function CreateCompanyForm() {
    const [companyName, setCompanyName] = useState("");
    const [about, setAbout] = useState("");
    const [prefectureId, setPrefectureId] = useState("");
    const [founders, setFounders] = useState<Founder[]>([]);
    const [ceoId, setCeoId] = useState<number>(0);
    const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    useEffect(() => {
        const fetchPrefectures = async () => {
            try {
                const req = AllPrefecturesRequest.create({});
                const response = await Hope.send(Request.create({ allPrefectures: req })) as {
                    allPrefectures?: AllPrefecturesResponse;
                };
                const received = response.allPrefectures?.prefectures ?? [];
                setPrefectures(received.map((p) => ({
                    id: Number(p.bankAccountId),
                    name: p.name,
                })));
            } catch (err) {
                console.error("Failed to load prefectures:", err);
            }
        };
        fetchPrefectures();
    }, []);

    const addFounder = () => {
        setFounders([...founders, Founder.create({ bankAccountId: 0, share: 0 })]);
    };

    const updateFounder = (index: number, field: "accountId" | "share", value: number) => {
        const updated = [...founders];
        if (field === "accountId") updated[index].bankAccountId = value;
        if (field === "share") updated[index].share = value;
        setFounders(updated);
    };

    const removeFounder = (index: number) => {
        setFounders(founders.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!companyName || !about || !prefectureId || founders.length === 0 || ceoId <= 0) {
            setMessage({ contents: "Все поля обязательны, включая генерального директора", status: AlertStatus.Error });
            return;
        }

        const invalidFounder = founders.find(
            (f) =>
                !f.bankAccountId || f.bankAccountId <= 0 ||
                !f.share || f.share <= 0 || f.share > 100
        );

        if (invalidFounder) {
            setMessage({
                contents: "ID учредителя должен быть > 0, а доля — от 1% до 100%.",
                status: AlertStatus.Error
            });
            return;
        }

        const request = CreateCompanyRequest.create({
            name: companyName,
            about: about,
            prefecture: prefectures.find((p) => p.id === parseInt(prefectureId))?.name ?? "",
            founders: [
                ...founders.map((f) =>
                    Founder.create({
                        bankAccountId: f.bankAccountId,
                        share: f.share / 100.0
                    })
                ),
            ],
            ceoBankAccountId: ceoId
        });

        const response = await Hope.send(Request.create({ createCompany: request })) as {
            createCompany?: CreateCompanyResponse;
        };

        switch (response.createCompany?.status) {
            case CreateCompanyResponse_Status.OK:
                setMessage({ contents: "Фирма успешно создана!", status: AlertStatus.Info });
                setCompanyName("");
                setAbout("");
                setPrefectureId("");
                setFounders([]);
                setCeoId(0);
                break;
            case CreateCompanyResponse_Status.MISSING_FOUNDERS:
                setMessage({ contents: "Не указаны учредители.", status: AlertStatus.Error });
                break;
            case CreateCompanyResponse_Status.DUPLICATE_FOUNDERS:
                setMessage({ contents: "Учредители дублируются.", status: AlertStatus.Error });
                break;
            case CreateCompanyResponse_Status.MISSING_PREFECTURE:
                setMessage({ contents: "Не выбрана префектура.", status: AlertStatus.Error });
                break;
            case CreateCompanyResponse_Status.DUPLICATE_NAME:
                setMessage({ contents: "Фирма с таким названием уже существует.", status: AlertStatus.Error });
                break;
            default:
                setMessage({ contents: "Неизвестная ошибка.", status: AlertStatus.Error });
        }
    };

    return (
        <Form className="new_company d-grid" onSubmit={handleSubmit}>
            {message && (
                <MessageAlert message={message.contents} status={message.status} />
            )}

            <div className="mb-3">
                <strong>
                    <label className="form-label">Название фирмы</label>
                </strong>
                <Form.Control
                    type="text"
                    className="form-control text-center"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                />
            </div>

            <div className="mb-3">
                <strong>
                    <label className="form-label">Описание</label>
                </strong>
                <Form.Control
                    type="text"
                    className="form-control text-center"
                    value={about}
                    onChange={(e) => setAbout(e.target.value)}
                />
            </div>

            <div className="mb-3">
                <strong>
                    <label className="form-label">Префектура</label>
                </strong>
                <Form.Select
                    className="form-select text-center"
                    value={prefectureId}
                    onChange={(e) => setPrefectureId(e.target.value)}
                >
                    <option value="">Выберите префектуру</option>
                    {prefectures.map((p) => (
                        <option key={p.id} value={p.id}>
                            {p.name}
                        </option>
                    ))}
                </Form.Select>
            </div>

            <div className="mb-3">
                <strong>
                    <label className="form-label">ID Генерального директора (CEO)</label>
                </strong>
                <Form.Control
                    type="number"
                    className="form-control text-center"
                    value={ceoId === 0 ? "" : ceoId}
                    onChange={(e) => setCeoId(Number(e.target.value))}
                    placeholder="Введите ID счета CEO"
                />
            </div>

            <div className="mb-3">
                <strong className="form-label d-block mb-2">Учредители</strong>

                {founders.map((founder, index) => (
                    <div key={index} className="d-flex gap-2 mb-2">
                        <input
                            type="text"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            className="form-control"
                            placeholder="ID учредителя"
                            value={founder.bankAccountId === 0 ? "" : String(founder.bankAccountId)}
                            onChange={(e) =>
                                updateFounder(index, "accountId", parseInt(e.target.value.replace(/^0+/, "") || "0", 10))
                            }
                        />
                        <input
                            type="text"
                            inputMode="decimal"
                            pattern="[0-9]*"
                            className="form-control"
                            placeholder="Доля (%)"
                            value={founder.share === 0 ? "" : String(founder.share)}
                            onChange={(e) =>
                                updateFounder(index, "share", parseInt(e.target.value.replace(/^0+/, "") || "0", 10))
                            }
                        />

                        <Button variant="outline-danger" onClick={() => removeFounder(index)}>
                            &times;
                        </Button>
                    </div>
                ))}

                <button
                    type="button"
                    className="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center"
                    onClick={addFounder}
                >
                    <span className="me-2 fs-4">+</span> Добавить учредителя
                </button>
            </div>

            <div className="d-grid gap-2 mb-4">
                <Button type="submit" className="btn btn-success">
                    Создать фирму
                </Button>
            </div>
        </Form>
    );
}
