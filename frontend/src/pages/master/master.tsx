import React from 'react';
import { useNavigate } from 'react-router-dom';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';

const MasterHomePage: React.FC = () => {
    const navigate = useNavigate();

    const NavButton = (path: string, label: string) => (
        <Button
            key={path}
            variant="contained"
            size="large"
            onClick={() => navigate(path)}
        >
            {label}
        </Button>
    );

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" align="center" gutterBottom>
                Личный кабинет мастера
            </Typography>

            <Stack spacing={2} sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}>
                {NavButton('/master/product/create', 'Зарегистрировать товар')}
                {NavButton('/master/product/all', 'Просмотреть все товары')}
                {NavButton('/master/resources', 'Про ресурсы/товары/энергию')}
                {NavButton('/master/prefecture/update', 'Сменить префектуру')}
                {NavButton('/master/company/create', 'Создать фирму')}
                {NavButton('/master/company/change-ceo', 'Сменить CEO')}
                {NavButton('/master/company/view-consumers', 'Сменить CEO')}
            </Stack>
        </Container>
    );
};

export default MasterHomePage;
