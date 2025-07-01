import React, { useState } from 'react';
import { useParams } from 'react-router-dom';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { CreateMoneyTransactionRequest } from '@app/codegen/app/protos/transaction/create';
import { TransactionStatusReason as TxStatus } from '@app/codegen/app/protos/types/transaction';

import { PageMode } from '@app/types';
import { useUser } from '@app/contexts/user';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';

interface MoneyTransferFormProps {
    mode: PageMode;
}

const MoneyTransferForm: React.FC<MoneyTransferFormProps> = ({ mode }) => {
    const params = useParams();
    const { bankAccountId } = useUser();

    const userBankAccount =
        mode === PageMode.Org ? Number(params.orgId) : bankAccountId;

    const [sellerAccount, setSellerAccount] = useState('');
    const [amount, setAmount] = useState('');
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    const getStatusMessage = (status: TxStatus | undefined): { contents: string; status: AlertStatus } => {
        switch (status) {
            case TxStatus.OK:
                return { contents: 'Перевод успешно отправлен', status: AlertStatus.Info };
            case TxStatus.CUSTOMER_IS_SELLER:
                return { contents: 'Ошибка: получатель совпадает с отправителем', status: AlertStatus.Error };
            case TxStatus.ALREADY_PROCESSED:
                return { contents: 'Ошибка: транзакция уже обработана', status: AlertStatus.Warning };
            case TxStatus.COUNT_OUT_OF_BOUNDS:
                return { contents: 'Ошибка: некорректное количество', status: AlertStatus.Error };
            case TxStatus.AMOUNT_OUT_OF_BOUNDS:
                return { contents: 'Ошибка: сумма вне допустимого диапазона', status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING:
                return { contents: 'Ошибка: ваш счёт не найден', status: AlertStatus.Error };
            case TxStatus.CUSTOMER_MISSING:
                return { contents: 'Ошибка: счёт получателя не найден', status: AlertStatus.Error };
            case TxStatus.SELLER_MISSING_GOODS:
                return { contents: 'Ошибка: недостаточно средств на вашем счёте', status: AlertStatus.Error };
            default:
                return { contents: 'Неизвестная ошибка при создании перевода', status: AlertStatus.Notice };
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);

        const seller = parseInt(sellerAccount, 10);
        const amt = parseInt(amount, 10);

        if (!userBankAccount || isNaN(seller) || isNaN(amt) || seller <= 0 || amt <= 0) {
            setMessage({
                contents: 'Введите корректные значения для счёта и суммы',
                status: AlertStatus.Error,
            });
            return;
        }

        try {
            const moneyTxReq = CreateMoneyTransactionRequest.create({
                sellerBankAccountId: userBankAccount,
                customerBankAccountId: seller,
                amount: amt,
            });

            const response = await Hope.send(
                Request.create({ createMoneyTransaction: moneyTxReq })
            );

            const resultStatus = getStatusMessage(
                response.createMoneyTransaction?.status as TxStatus | undefined
            );

            setMessage(resultStatus);

            if (response.createMoneyTransaction?.status === TxStatus.OK) {
                setSellerAccount('');
                setAmount('');
            }
        } catch (err) {
            console.error(err);
            setMessage({
                contents: 'Ошибка при отправке запроса',
                status: AlertStatus.Error,
            });
        }
    };

    if (!userBankAccount || isNaN(userBankAccount)) {
        return <MessageAlert message="Некорректный ID счёта" status={AlertStatus.Error} />;
    }

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
                mt: 4,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
            }}
        >
            <MessageAlert
                message={message?.contents ?? ''}
                status={message?.status ?? AlertStatus.Info}
            />

            <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Ваш счёт:</strong> {userBankAccount}
            </Typography>

            <TextField
                label="Счёт получателя"
                type="number"
                placeholder="Введите счёт получателя"
                value={sellerAccount}
                onChange={(e) => setSellerAccount(e.target.value)}
                fullWidth
                sx={{ mb: 3 }}
            />

            <TextField
                label="Сумма"
                type="number"
                placeholder="Введите сумму перевода"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                fullWidth
                sx={{ mb: 3 }}
            />

            <Button
                type="submit"
                variant="contained"
                color="success"
                size="large"
                fullWidth
            >
                Подтверждаю
            </Button>
        </Box>
    );
};

export default MoneyTransferForm;
