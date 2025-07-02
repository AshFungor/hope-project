import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { AllCompaniesRequest, AllCompaniesResponse } from '@app/codegen/app/protos/company/all';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Box from '@mui/material/Box';

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
        <Container sx={{ mt: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Typography variant="h4">
                    <strong>Список доступных фирм</strong>
                </Typography>
            </Box>

            <List sx={{ maxWidth: 600, mx: 'auto' }}>
                {companies.map((company) => (
                    <ListItemButton
                        key={company.bankAccountId}
                        onClick={() => handleClick(company.bankAccountId)}
                        sx={{ textAlign: 'center' }}
                    >
                        <ListItemText primary={company.name} />
                    </ListItemButton>
                ))}
            </List>
        </Container>
    );
}
