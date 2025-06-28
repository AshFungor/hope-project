import React from "react";
import { useNavigate } from "react-router-dom";

const MasterHomePage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="container py-4">
            <h1 className="mb-4 text-center">Личный кабинет мастера</h1>

            <div className="d-grid gap-3 mb-4">
                <button
                    className="btn btn-outline-dark btn-lg"
                    onClick={() => navigate("/master/product/create")}
                >
                    Зарегистрировать товар
                </button>

                <button
                    className="btn btn-outline-dark btn-lg"
                    onClick={() => navigate("/master/resources")}
                >
                    Про ресурсы/товары/энергию
                </button>

                <button
                    className="btn btn-outline-dark btn-lg"
                    onClick={() => navigate("/master/prefecture/update")}
                >
                    Сменить префектуру
                </button>

                <button
                    className="btn btn-outline-dark btn-lg"
                    onClick={() => navigate("/master/company/create")}
                >
                    Создать фирму
                </button>
            </div>
        </div>
    );
};

export default MasterHomePage;
