import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import Paper from '@mui/material/Paper';
import Pagination from '@mui/material/Pagination';
import Box from '@mui/material/Box';

import { PageMode } from '@app/types';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { Transaction, Transaction_Status } from '@app/codegen/app/protos/types/transaction';
import { ViewTransactionsRequest } from '@app/codegen/app/protos/transaction/history';

import { Transaction as TransactionLocal } from '@app/api/sub/transaction';
import { useUser } from '@app/contexts/user';

interface TransactionHistoryProps {
    mode: PageMode;
}

const Row: React.FC<{ transaction: Transaction }> = ({ transaction }) => {
    const t = new TransactionLocal(
        transaction.sellerBankAccountId,
        transaction.customerBankAccountId,
        transaction.product,
        transaction.count,
        transaction.amount,
        transaction.status,
        transaction.transactionId,
        transaction.createdAt,
        transaction.updatedAt,
        transaction.side,
        transaction.isMoney
    );

    let bgColor = '';
    if (transaction.status === Transaction_Status.ACCEPTED) {
        bgColor = '#d4edda'; // green-ish
    } else if (transaction.status === Transaction_Status.REJECTED) {
        bgColor = '#f8d7da'; // red-ish
    }

    return (
        <TableRow sx={{ backgroundColor: bgColor }}>
            <TableCell>{t.transactionId}</TableCell>
            <TableCell>{t.product}</TableCell>
            {t.isMoney ? (
                <TableCell colSpan={2}>{t.count}</TableCell>
            ) : (
                <>
                    <TableCell>{t.count}</TableCell>
                    <TableCell>{t.amount}</TableCell>
                </>
            )}
            <TableCell>{t.stringStatus()}</TableCell>
            <TableCell>{t.createdAt}</TableCell>
            <TableCell>{t.updatedAt}</TableCell>
            <TableCell>{t.side}</TableCell>
            <TableCell>{(t.side == 'seller') ? t.customerBankAccountId : t.sellerBankAccountId}</TableCell>
        </TableRow>
    );
};

const TransactionsTable: React.FC<{ transactions: Transaction[] }> = ({ transactions }) => (
    <Box sx={{ overflowX: 'auto', width: '100%' }}>
        <Table sx={{ minWidth: 800 }}>
            <TableHead>
                <TableRow>
                    <TableCell>Номер транзакции</TableCell>
                    <TableCell>Товар</TableCell>
                    <TableCell>Количество</TableCell>
                    <TableCell>Цена</TableCell>
                    <TableCell>Статус</TableCell>
                    <TableCell>Создано</TableCell>
                    <TableCell>Обновлено</TableCell>
                    <TableCell>Сторона сделки</TableCell>
                    <TableCell>Счет второй стороны</TableCell>
                </TableRow>
            </TableHead>
            <TableBody>
                {transactions.map((t) => (
                    <Row key={t.transactionId} transaction={t} />
                ))}
            </TableBody>
        </Table>
    </Box>
);


export default function TransactionHistory({ mode }: TransactionHistoryProps) {
    const params = useParams();
    const { bankAccountId } = useUser();

    const effectiveAccountId =
        mode === PageMode.Org
            ? Number(params.orgId)
            : bankAccountId;

    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [page, setPage] = useState(0);
    const pageSize = 20;

    useEffect(() => {
        if (!effectiveAccountId) return;

        const fetchTransactions = async () => {
            const viewReq: ViewTransactionsRequest = {
                account: effectiveAccountId,
            };

            const response = await Hope.sendTyped(
                Request.create({ viewTransactionHistory: viewReq }),
                'viewTransactionHistory'
            );

            const txs = response.transactions ?? [];
            setTransactions([...txs].sort((a, b) =>
                (b.updatedAt || '').localeCompare(a.updatedAt || '')
            ));
        };

        fetchTransactions();
    }, [effectiveAccountId]);

    if (!effectiveAccountId) return null;

    const paginated = transactions.slice(page * pageSize, (page + 1) * pageSize);
    const totalPages = Math.ceil(transactions.length / pageSize);

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" align="center" gutterBottom>
                История транзакций
            </Typography>

            <Paper sx={{ width: '100%', overflow: 'auto', mb: 2 }}>
                <TransactionsTable transactions={paginated} />
            </Paper>

            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Pagination
                    count={totalPages}
                    page={page + 1}
                    onChange={(_, value) => setPage(value - 1)}
                    color="primary"
                />
            </Box>
        </Container>
    );
}
