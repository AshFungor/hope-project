import { Goal } from '@app/api/sub/goal';

import Box from '@mui/material/Box';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';

interface GoalSelectionProperties {
    goal: Goal | null;
    balance: number;
}

export default function GoalSection({ goal, balance }: GoalSelectionProperties) {
    if (!goal || goal.value === null) {
        return (
            <Box
                sx={{
                    textAlign: 'center',
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    pb: 3,
                    mb: 3,
                }}
            >
                <Typography variant="body2" color="text.secondary">
                    Цель не задана
                </Typography>
            </Box>
        );
    }

    const progress = goal.getRate(balance);

    return (
        <Box
            sx={{
                textAlign: 'center',
                borderBottom: '1px solid',
                borderColor: 'divider',
                pb: 3,
                mb: 3,
            }}
        >
            <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>Цель по доходу в день:</strong> <b>{goal.value}</b> Ψ
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ flexGrow: 1 }}>
                    <LinearProgress
                        variant="determinate"
                        value={progress}
                        sx={{ height: 10, borderRadius: 5 }}
                        color="success"
                    />
                </Box>
                <Typography variant="body2" sx={{ minWidth: 35 }}>
                    {`${progress}%`}
                </Typography>
            </Box>
        </Box>
    );
}
