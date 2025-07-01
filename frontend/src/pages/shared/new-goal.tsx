import React, { useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';

import BalanceSection from '@app/widgets/shared/balance';
import { Goal } from '@app/codegen/app/protos/types/goal';
import { CreateGoalRequest } from '@app/codegen/app/protos/goal/create';

import { PageMode } from '@app/types';
import { useUser } from '@app/contexts/user';

interface GoalFormPageProps {
    mode: PageMode;
}

export default function GoalFormPage({ mode }: GoalFormPageProps) {
    const params = useParams();
    const { bankAccountId } = useUser();
    const navigate = useNavigate();
    const location = useLocation();

    const effectiveAccountId =
        mode === PageMode.Org
            ? Number(params.orgId)
            : bankAccountId;

    const paramsSearch = new URLSearchParams(location.search);
    const current = Number(paramsSearch.get('current'));

    const [value, setValue] = useState<number | undefined>();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!effectiveAccountId) {
            throw new Error('No effective account ID found');
        }

        const goal = Goal.create({
            bankAccountId: effectiveAccountId,
            value: value,
        });
        const createGoalReq = CreateGoalRequest.create({ goal });

        await Hope.send(Request.create({ createGoal: createGoalReq }));
        navigate(-1);
    };

    const handleSkip = async () => {
        if (!effectiveAccountId) {
            throw new Error('No effective account ID found');
        }

        const goal = Goal.create({
            bankAccountId: effectiveAccountId,
            value: 0,
        });
        const createGoalReq = CreateGoalRequest.create({ goal });

        await Hope.send(Request.create({ createGoal: createGoalReq }));
        navigate(-1);
    };

    if (!effectiveAccountId) {
        return <Typography>Не удалось определить счёт</Typography>;
    }

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ maxWidth: 400, mx: 'auto', mt: 4 }}
        >
            <Stack spacing={3}>
                <Typography>
                    <strong>Ваш счёт:</strong> {effectiveAccountId}
                </Typography>

                <BalanceSection current={current} />

                <TextField
                    type="number"
                    label="Цель на сегодня (в надиках)"
                    placeholder="Введите цель"
                    value={value ?? ''}
                    onChange={(e) => setValue(Number(e.target.value))}
                    fullWidth
                />

                <Stack direction="row" spacing={2}>
                    <Button type="submit" variant="contained" color="success" size="small">
                        Установить цель
                    </Button>
                    <Button type="button" variant="outlined" color="secondary" size="small" onClick={handleSkip}>
                        Пропустить
                    </Button>
                </Stack>
            </Stack>
        </Box>
    );
}
