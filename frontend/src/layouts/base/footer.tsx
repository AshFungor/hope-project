import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

export default function Footer() {
    return (
        <Box
            component="footer"
            sx={{
                py: 3,
                mt: 'auto',
                textAlign: 'center',
                borderTop: 1,
                borderColor: 'divider',
            }}
        >
            <Typography variant="body2" color="text.secondary">
                © 2024 Надежда
            </Typography>
        </Box>
    );
}
