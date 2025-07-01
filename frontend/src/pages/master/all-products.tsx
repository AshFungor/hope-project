import React, { useEffect, useState } from 'react';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import { Product } from '@app/codegen/app/protos/types/product';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

export default function AllProductsPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    useEffect(() => {
        const fetchAllProducts = async () => {
            try {
                const response = await Hope.sendTyped(Request.create({ allProducts: {} }), 'allProducts');
                setProducts(response.products ?? []);
            } catch (err) {
                console.error(err);
                setMessage({
                    contents: 'Ошибка при загрузке списка товаров',
                    status: AlertStatus.Error,
                });
            }
        };

        fetchAllProducts();
    }, []);

    const getRowColor = (level: number): string => {
        switch (level) {
            case 1:
                return '#d1ecf1'; // light info
            case 2:
                return '#cce5ff'; // light primary
            case 4:
                return '#fff3cd'; // light warning
            default:
                return '#f8f9fa'; // light gray
        }
    };

    const categories = Array.from(new Set(products.map((p) => p.category)));

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Все товары в игре
            </Typography>

            <MessageAlert message={message?.contents ?? null} status={message?.status} />

            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Название</TableCell>
                        <TableCell>Категория</TableCell>
                        <TableCell>Уровень</TableCell>
                        <TableCell>Можно потреблять</TableCell>
                    </TableRow>
                </TableHead>

                {categories.map((category) => (
                    <React.Fragment key={category ?? ''}>
                        <TableHead>
                            <TableRow>
                                <TableCell colSpan={4}>
                                    <Typography variant="h6">{category}</Typography>
                                </TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {products
                                .filter((p) => p.category === category)
                                .map((p) => (
                                    <TableRow
                                        key={p.name}
                                        sx={{ backgroundColor: getRowColor(p.level ?? 0) }}
                                    >
                                        <TableCell>{p.name}</TableCell>
                                        <TableCell>{p.category}</TableCell>
                                        <TableCell>{p.level}</TableCell>
                                        <TableCell>{p.consumable ? 'Да' : 'Нет'}</TableCell>
                                    </TableRow>
                                ))}
                        </TableBody>
                    </React.Fragment>
                ))}
            </Table>
        </Container>
    );
}
