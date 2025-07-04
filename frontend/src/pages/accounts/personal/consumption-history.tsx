import React, { useEffect, useState } from 'react';
import { useUser } from '@app/contexts/user';

import {
    Box,
    Typography,
    CircularProgress,
    Card,
    CardContent,
    Stack,
} from '@mui/material';

import { Request } from '@app/codegen/app/protos/request';
import { Hope } from '@app/api/api';
import {
    ConsumptionHistoryRequest,
    ConsumptionHistoryResponse_ConsumptionEntry
} from '@app/codegen/app/protos/product/history';

import { MessageAlert } from '@app/widgets/shared/alert';

export default function ConsumptionHistoryPage() {
    const { bankAccountId } = useUser();
    const [loading, setLoading] = useState(true);
    const [entries, setEntries] = useState<ConsumptionHistoryResponse_ConsumptionEntry[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!bankAccountId) return;

        const fetchHistory = async () => {
            try {
                const req = ConsumptionHistoryRequest.create({
                    bankAccountId: bankAccountId,
                });
                const resp = await Hope.sendTyped(Request.create({ viewConsumptionHistory: req }), "viewConsumptionHistory");
                setEntries(resp?.entries?.entries ?? []);
            } catch (err) {
                setError("Failed to load data.");
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [bankAccountId]);

    const getGradient = (category: string | undefined) => {
        switch (category) {
            // design better
            case 'ENERGY':
                return 'linear-gradient(135deg, #fff7ae, #ffe08a)';
            case 'FOOD':
                return 'linear-gradient(135deg, #ffe0e0, #ffcccc)';
            case 'WATER':
                return 'linear-gradient(135deg, #d0f0ff, #a0d8ef)';
            default:
                return 'linear-gradient(135deg, #f0f0f0, #e0e0e0)';
        }
    };

    return (
        <Box sx={{ width: '100%', mt: 2 }}>
            <Typography variant="h4" gutterBottom>
                История потребления
            </Typography>

            {loading && <CircularProgress />}
            {error && <MessageAlert message={error} />}

            {!loading && !error && (
                <Stack spacing={2}>
                    {entries.map((entry, index) => (
                        <Card
                            key={index}
                            variant="outlined"
                            sx={{
                                position: 'relative',
                                overflow: 'hidden',
                                background: getGradient(entry?.product?.category),
                            }}
                        >
                            <CardContent>
                                <Typography variant="subtitle2" color="text.secondary">
                                    Дата: {entry.consumedAt}
                                </Typography>

                                <Typography variant="h6" gutterBottom>
                                    {entry?.product?.name ?? 'Неизвестный продукт'}
                                </Typography>

                                <Typography variant="body1">
                                    Количество: <strong>{entry.count}</strong>
                                </Typography>

                                <Typography
                                    variant="caption"
                                    sx={{
                                        position: 'absolute',
                                        top: 8,
                                        right: 16,
                                        fontSize: '0.9rem',
                                        backgroundColor: 'rgba(255, 255, 255, 0.6)',
                                        borderRadius: '12px',
                                        px: 1.5,
                                        py: 0.5,
                                    }}
                                >
                                    {entry?.product?.category ?? 'Неизвестно'}
                                </Typography>
                            </CardContent>
                        </Card>
                    ))}
                </Stack>
            )}
        </Box>
    );
}
