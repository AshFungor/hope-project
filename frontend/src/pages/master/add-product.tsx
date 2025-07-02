import React, { useState } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';
import {
    CreateProductRequest,
    CreateProductResponse,
} from '@app/codegen/app/protos/product/create';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

export default function NewProductPage() {
    const [productName, setProductName] = useState('');
    const [category, setCategory] = useState('');
    const [level, setLevel] = useState('');
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!productName || !category || !level) {
            setMessage({ contents: 'Все поля обязательны!', status: AlertStatus.Error });
            return;
        }

        const product = {
            name: productName,
            category: category,
            level: parseInt(level, 10),
        };

        const req = CreateProductRequest.create({ product });

        const response = await Hope.send(Request.create({ createProduct: req })) as {
            createProduct?: CreateProductResponse;
        };

        if (response.createProduct?.status) {
            setMessage({ contents: 'Продукт успешно создан!', status: AlertStatus.Info });
            setProductName('');
            setCategory('');
            setLevel('');
        } else {
            setMessage({ contents: 'Ошибка: продукт не удалось создать.', status: AlertStatus.Error });
        }
    };

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" align="center" sx={{ mb: 4 }}>
                Новый продукт
            </Typography>

            <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 400, mx: 'auto' }}>
                {message && (
                    <MessageAlert message={message.contents} status={message.status} />
                )}

                <Stack spacing={3} sx={{ mb: 4 }}>
                    <TextField
                        label="Название продукта"
                        value={productName}
                        onChange={(e) => setProductName(e.target.value)}
                        placeholder="Введите название"
                        fullWidth
                    />

                    <FormControl fullWidth>
                        <InputLabel id="category-label">Категория</InputLabel>
                        <Select
                            labelId="category-label"
                            value={category}
                            label="Категория"
                            onChange={(e) => setCategory(e.target.value)}
                        >
                            <MenuItem value="">Выберите категорию</MenuItem>
                            <MenuItem value="Energy">ENERGY</MenuItem>
                            <MenuItem value="Resource">FOOD</MenuItem>
                            <MenuItem value="ProductTech">TECHNIC</MenuItem>
                            <MenuItem value="ProductClothes">CLOTHES</MenuItem>
                        </Select>
                    </FormControl>

                    <FormControl fullWidth>
                        <InputLabel id="level-label">Уровень</InputLabel>
                        <Select
                            labelId="level-label"
                            value={level}
                            label="Уровень"
                            onChange={(e) => setLevel(e.target.value)}
                        >
                            <MenuItem value="">Выберите уровень</MenuItem>
                            {[0, 1, 2, 3, 4].map((lvl) => (
                                <MenuItem key={lvl} value={lvl}>{lvl}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Stack>

                <Button type="submit" variant="contained" color="primary" fullWidth>
                    Создать
                </Button>
            </Box>
        </Container>
    );
}
