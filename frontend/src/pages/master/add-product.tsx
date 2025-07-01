import React, { useState } from "react";
import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import {
    CreateProductRequest,
    CreateProductResponse,
} from "@app/codegen/app/protos/product/create";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

const NewProductForm: React.FC = () => {
    const [productName, setProductName] = useState("");
    const [category, setCategory] = useState("");
    const [level, setLevel] = useState("");
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!productName || !category || !level) {
            setMessage({ contents: "Все поля обязательны!", status: AlertStatus.Error });
            return;
        }

        const product = {
            name: productName,
            category: category,
            level: parseInt(level, 10),
        };

        const req = CreateProductRequest.create({ product });

        const response = await Hope.send(Request.create({ createProduct: req })) as {
            createProduct?: CreateProductResponse;
        };

        if (response.createProduct?.status) {
            setMessage({ contents: "Продукт успешно создан!", status: AlertStatus.Info });
            setProductName("");
            setCategory("");
            setLevel("");
        } else {
            setMessage({ contents: "Ошибка: продукт не удалось создать.", status: AlertStatus.Error });
        }
    };

    return (
        <form className="new_product d-grid" onSubmit={handleSubmit}>
            {message && (
                <MessageAlert message={message.contents} status={message.status} />
            )}

            <div className="mb-3">
                <label className="form-label">Название продукта</label>
                <input
                    type="text"
                    className="form-control"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="Введите название"
                />
            </div>

            <div className="mb-3">
                <label className="form-label">Категория</label>
                <select
                    className="form-select"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                >
                    <option value="">Выберите категорию</option>
                    <option value="Energy">ENERGY</option>
                    <option value="Resource">FOOD</option>
                    <option value="Product">TECHNIC</option>
                    <option value="Product">CLOTHES</option>
                </select>
            </div>

            <div className="mb-3">
                <label className="form-label">Уровень</label>
                <select
                    className="form-select"
                    value={level}
                    onChange={(e) => setLevel(e.target.value)}
                >
                    <option value="">Выберите уровень</option>
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2">2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                </select>
            </div>

            <div className="d-grid gap-2 mb-4">
                <button type="submit" className="btn btn-success">
                    Создать
                </button>
            </div>
        </form>
    );
};

export default NewProductForm;
