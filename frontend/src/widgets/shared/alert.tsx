import React from 'react';

import MuiAlert, { AlertColor } from '@mui/material/Alert';
import Box from '@mui/material/Box';

export enum AlertStatus {
    Error = 'error',
    Warning = 'warning',
    Info = 'info',
    Notice = 'notice',
}

interface MessageAlertProperties {
    message: string | null;
    status?: AlertStatus;
}

export const MessageAlert: React.FC<MessageAlertProperties> = ({
    message,
    status = AlertStatus.Error,
}) => {
    if (!message) {
        return null;
    }

    const severityMap: Record<AlertStatus, AlertColor> = {
        [AlertStatus.Error]: 'error',
        [AlertStatus.Warning]: 'warning',
        [AlertStatus.Info]: 'info',
        [AlertStatus.Notice]: 'success',
    };

    const severity: AlertColor = severityMap[status] ?? 'info';

    return (
        <Box sx={{ mb: 2 }}>
            <MuiAlert severity={severity} className="fade-in">
                {message}
            </MuiAlert>
        </Box>
    );
};

export default MessageAlert;
