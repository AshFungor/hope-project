import { useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

const HomePage = () => {
    const navigate = useNavigate();
    const { currentUser } = useUser();

    const NavButton = (path: string, label: string) => (
        <Button
            variant="outlined"
            size="large"
            onClick={() => navigate(path)}
            sx={{ mb: 2 }}
        >
            {label}
        </Button>
    );

    return (
        <Box sx={{ overflow: 'hidden', p: 2 }}>
            <Stack spacing={2}>
                {NavButton('/personal/index', 'Личный кабинет')}
                {NavButton('/companies', 'Фирмы')}
                {NavButton('/prefecture/index', 'Префектура')}
                {NavButton('/city_hall/index', 'Мэрия')}
                {currentUser?.isAdmin && NavButton('/master/index', 'Мастер игры')}
            </Stack>
        </Box>
    );
};

export default HomePage;
