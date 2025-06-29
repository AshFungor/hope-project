import React from "react";

export enum AlertStatus {
    Error = "error",
    Warning = "warning",
    Info = "info",
    Notice = "notice",
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

    const alertClass = {
        [AlertStatus.Error]: "alert-danger",
        [AlertStatus.Warning]: "alert-warning",
        [AlertStatus.Info]: "alert-info",
        [AlertStatus.Notice]: "alert-primary",
    }[status] || "alert-secondary";

    return (
        <div className={`alert ${alertClass} fade-in`} role="alert">
            {message}
        </div>
    );
};

export default MessageAlert;
