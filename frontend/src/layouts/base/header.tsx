import { useNavigate } from 'react-router-dom';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { LogoutRequest } from '@app/codegen/app/protos/session/logout';

import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';

export default function Header({ showLogout = false }: { showLogout?: boolean }) {
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            const logoutRequest = LogoutRequest.create({});
            await Hope.send(Request.create({ logout: logoutRequest }));
        } catch (err) {
            console.warn('Logout failed:', err);
        } finally {
            navigate('/auth/login');
        }
    };

    return (
        <AppBar
            position="static"
            color="default"
            enableColorOnDark
            sx={{
                px: 3,
                py: 1,
                borderBottom: 1,
                borderColor: 'divider',
                bgcolor: 'black',
            }}
        >
            <Toolbar disableGutters sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Box component="a" href="/" sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
                <Box
                    component="img"
                    src="/images/logo.png"
                    alt="Logo"
                    sx={{
                        height: 'auto',
                        maxHeight: 40,
                        width: '100%',
                        maxWidth: 200,
                        objectFit: 'contain',
                    }}
                />
                </Box>
                {showLogout && (
                    <Button
                        variant="outlined"
                        color="primary"
                        onClick={handleLogout}
                        sx={{ ml: 'auto' }}
                    >
                        Выход
                    </Button>
                )}
            </Toolbar>
        </AppBar>
    );
}
