import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { AllCompaniesRequest, AllCompaniesResponse } from "@app/codegen/app/protos/company/all";

interface Company {
    bankAccountId: number;
    name: string;
}

export default function CompanyListPage() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        const loadCompanies = async () => {
            const req: AllCompaniesRequest = { globally: true };
            const response = await Hope.send(Request.create({ allCompanies: req })) as {
                allCompanies?: AllCompaniesResponse;
            };

            const loaded = response.allCompanies?.companies ?? [];
            setCompanies(
                loaded.map(c => ({
                    bankAccountId: Number(c.bankAccountId),
                    name: c.name,
                }))
            );
        };

        loadCompanies();
    }, []);

    const handleClick = (companyId: number) => {
        navigate(`/company/${companyId}`);
    };

    return (
        <div className="container mt-4">
            <div className="text-wrap text-center d-flex flex-wrap align-items-center justify-content-center mb-3">
                <h3><strong>Список доступных фирм</strong></h3>
            </div>

            <div className="list-group">
                {companies.map((company) => (
                    <button
                        key={company.bankAccountId}
                        type="button"
                        className="list-group-item list-group-item-action text-center"
                        onClick={() => handleClick(company.bankAccountId)}
                    >
                        {company.name}
                    </button>
                ))}
            </div>
        </div>
    );
}
