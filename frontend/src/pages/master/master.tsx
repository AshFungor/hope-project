import React from "react";
import { useNavigate } from "react-router-dom";

const MasterHomePage: React.FC = () => {
    const navigate = useNavigate();

    const Button = (path: string, label: string) => (
        <button
            className="btn btn-outline-dark btn-lg mb-3"
            onClick={() => navigate(path)}
        >
            {label}
        </button>
    );

    return (
        <div className="container overflow-hidden">
            <h1 className="mb-4 text-center">Личный кабинет мастера</h1>

            <div className="d-grid gap-2 d-mb-block mb-4">
                {Button("/master/product/create", "Зарегистрировать товар")}
                {Button("/master/product/all", "Просмотреть все товары")}
                {Button("/master/resources", "Про ресурсы/товары/энергию")}
                {Button("/master/prefecture/update", "Сменить префектуру")}
                {Button("/master/company/create", "Создать фирму")}
            </div>
        </div>
    );
};

export default MasterHomePage;
