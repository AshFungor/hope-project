import React, { useState, useEffect } from "react";
import { Form, Button } from "react-bootstrap";

interface Prefecture {
    id: number;
    name: string;
}

const CreateCompanyForm: React.FC = () => {
    const [companyName, setCompanyName] = useState("");
    const [about, setAbout] = useState("");
    const [founders, setFounders] = useState("");
    const [prefectureId, setPrefectureId] = useState("");
    const [messages, setMessages] = useState<{ category: string; message: string }[]>([]);
    const [prefectures, setPrefectures] = useState<Prefecture[]>([]);

    useEffect(() => {
        // Replace with your real API call for all prefectures
        // For example:
        // const response = await Hope.send(Request.create({ allPrefectures: {} }));
        // setPrefectures(response.allPrefectures?.prefectures ?? []);
        setPrefectures([
            { id: 1, name: "Префектура 1" },
            { id: 2, name: "Префектура 2" },
        ]);
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (!companyName || !about || !founders || !prefectureId) {
            setMessages([{ category: "danger", message: "Все поля обязательны!" }]);
            return;
        }

        console.log("Submitting:", {
            companyName,
            about,
            founders,
            prefectureId,
        });

        // Replace with your backend POST logic
        setMessages([{ category: "success", message: "Фирма успешно создана!" }]);

        // Optionally reset
        setCompanyName("");
        setAbout("");
        setFounders("");
        setPrefectureId("");
    };

    return (
        <Form className="new_company d-grid" onSubmit={handleSubmit}>
            {messages.length > 0 && (
                <ul className="flashes">
                    {messages.map((m, i) => (
                        <li key={i} className={`alert alert-${m.category}`}>
                            {m.message}
                        </li>
                    ))}
                </ul>
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
                    <label className="form-label">Учредители</label>
                </strong>
                <Form.Control
                    type="text"
                    className="form-control text-center"
                    value={founders}
                    onChange={(e) => setFounders(e.target.value)}
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

            <div className="d-grid gap-2 mb-4">
                <Button type="submit" className="btn btn-success">
                    Создать
                </Button>
            </div>
        </Form>
    );
};

export default CreateCompanyForm;
