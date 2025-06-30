import React, { useEffect, useState } from "react";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { Product } from "@app/codegen/app/protos/types/product";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

export default function AllProductsPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    useEffect(() => {
        const fetchAllProducts = async () => {
            try {
                const response = await Hope.sendTyped(Request.create({ allProducts: {} }), "allProducts");
                setProducts(response.products ?? []);
            } catch (err) {
                console.error(err);
                setMessage({
                    contents: "Ошибка при загрузке списка товаров",
                    status: AlertStatus.Error,
                });
            }
        };

        fetchAllProducts();
    }, []);

    const getRowClass = (level: number): string => {
        switch (level) {
            case 1:
                return "table-info";
            case 2:
                return "table-primary";
            case 4:
                return "table-warning";
            default:
                return "table-light";
        }
    };

    const categories = Array.from(new Set(products.map((p) => p.category)));

    return (
        <div className="container mt-4">
            <h2>Все товары в игре</h2>

            <MessageAlert message={message?.contents ?? null} status={message?.status} />

            <table className="table">
                <thead>
                    <tr>
                        <th>Название</th>
                        <th>Категория</th>
                        <th>Уровень</th>
                        <th>Можно потреблять</th>
                    </tr>
                </thead>

                {categories.map((category) => (
                    <React.Fragment key={category ?? ""}>
                        <thead>
                            <tr>
                                <th colSpan={4}>{category}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products
                                .filter((p) => p.category === category)
                                .map((p) => (
                                    <tr
                                        key={p.name}
                                        className={getRowClass(p.level ?? 0)}
                                    >
                                        <td>{p.name}</td>
                                        <td>{p.category}</td>
                                        <td>{p.level}</td>
                                        <td>{p.consumable ? "Да" : "Нет"}</td>
                                    </tr>
                                ))}
                        </tbody>
                    </React.Fragment>
                ))}
            </table>
        </div>
    );
}
