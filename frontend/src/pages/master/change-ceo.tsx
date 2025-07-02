import React, { useState } from "react";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { MasterChangeCEORequest } from "@app/codegen/app/protos/company/employ";

import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

export default function MasterChangeCEOPage() {
    const [companyId, setCompanyId] = useState("");
    const [newCeoId, setNewCeoId] = useState("");
    const [message, setMessage] = useState<string | null>(null);
    const [messageStatus, setMessageStatus] = useState<AlertStatus>(AlertStatus.Info);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const req = MasterChangeCEORequest.create({
            companyId: Number(companyId),
            newCeoId: Number(newCeoId),
        });

        const response = await Hope.send(Request.create({ masterChangeCeo: req }));

        if (response.masterChangeCeo?.ok) {
            setMessage("CEO успешно изменён!");
            setMessageStatus(AlertStatus.Notice);
            setCompanyId("");
            setNewCeoId("");
        } else {
            setMessage("Ошибка при смене CEO");
            setMessageStatus(AlertStatus.Error);
        }
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: "auto", mt: 4 }}>
            {message && (
                <MessageAlert message={message} status={messageStatus} />
            )}

            <TextField
                label="ID Компании (по bank_account_id)"
                type="number"
                value={companyId}
                onChange={(e) => setCompanyId(e.target.value)}
                fullWidth
                sx={{ mb: 3 }}
            />
            <TextField
                label="ID нового CEO (по bank_account_id)"
                type="number"
                value={newCeoId}
                onChange={(e) => setNewCeoId(e.target.value)}
                fullWidth
                sx={{ mb: 3 }}
            />
            <Button type="submit" variant="contained" fullWidth>
                Изменить CEO
            </Button>
        </Box>
    );
}
