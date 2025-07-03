import React, { useEffect, useState } from "react";

import {
    Box,
    Container,
    Typography,
    Table,
    TableHead,
    TableRow,
    TableCell,
    TableBody,
    Select,
    MenuItem,
    Button,
    FormControl,
    InputLabel,
    Stack,
} from "@mui/material";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import {
    ViewConsumersRequest,
    CollectConsumersRequest,
} from "@app/codegen/app/protos/product/consumption";

import { Consumer } from "@app/codegen/app/protos/types/consumer";
import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

export default function ViewConsumersPage() {
    const [categories, setCategories] = useState<string[]>([]);
    const [consumers, setConsumers] = useState<Consumer[]>([]);
    const [currentCategory, setCurrentCategory] = useState("all");
    const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

    // Fetch categories dynamically
    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await Hope.sendTyped(Request.create({ allProducts: {} }), "allProducts");
                const products = response.products ?? [];

                const uniqueConsumable = Array.from(
                    new Set(
                        products
                            .filter((p) => p.consumable)
                            .map((p) => p.category.toUpperCase())
                    )
                );

                setCategories(uniqueConsumable);
            } catch (err) {
                console.error(err);
                setMessage({
                    contents: "Ошибка при загрузке списка категорий",
                    status: AlertStatus.Error,
                });
            }
        };

        fetchCategories();
    }, []);

    const fetchConsumers = async (category: string) => {
        const req = ViewConsumersRequest.create({ category });
        const response = await Hope.sendTyped(Request.create({ viewConsumers: req }), "viewConsumers");
        setConsumers(response.consumers ?? []);
    };

    useEffect(() => {
        fetchConsumers(currentCategory);
    }, [currentCategory]);

    const handleCollect = async () => {
        const req = CollectConsumersRequest.create({
            userIds: consumers.map((u) => u.user?.bankAccountId ?? 0),
            categories: currentCategory === "all" ? categories : [currentCategory],
        });

        const response = await Hope.sendTyped(Request.create({ collectConsumers: req }), "collectConsumers");

        setMessage({
            contents: response.message,
            status: response.success ? AlertStatus.Info : AlertStatus.Error,
        });

        await fetchConsumers(currentCategory);
    };

    return (
        <Container sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Просмотр потребления
            </Typography>

            <MessageAlert
                message={message?.contents ?? null}
                status={message?.status ?? AlertStatus.Info}
            />

            <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
                <FormControl>
                    <InputLabel>Категория</InputLabel>
                    <Select
                        value={currentCategory}
                        label="Категория"
                        onChange={(e) => setCurrentCategory(e.target.value)}
                        sx={{ minWidth: 200 }}
                    >
                        <MenuItem value="all">Все</MenuItem>
                        {categories.map((cat) => (
                            <MenuItem key={cat} value={cat}>
                                {cat}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>

                <Button variant="contained" color="success" onClick={() => fetchConsumers(currentCategory)}>
                    Обновить
                </Button>

                <Button variant="contained" color="primary" onClick={handleCollect}>
                    Списать
                </Button>
            </Stack>

            <Box sx={{ overflowX: "auto" }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Банковский счет</TableCell>
                            <TableCell>Фамилия</TableCell>
                            <TableCell>Имя</TableCell>
                            <TableCell>Отчество</TableCell>
                            {categories.map(
                                (cat) =>
                                    (currentCategory === "all" || currentCategory === cat) && (
                                        <TableCell key={cat}>{cat}</TableCell>
                                    )
                            )}
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {consumers.map((c) => (
                            <TableRow key={c.user?.bankAccountId}>
                                <TableCell>{c.user?.bankAccountId}</TableCell>
                                <TableCell>{c.user?.lastName}</TableCell>
                                <TableCell>{c.user?.name}</TableCell>
                                <TableCell>{c.user?.patronymic}</TableCell>
                                {categories.map(
                                    (cat) =>
                                        (currentCategory === "all" || currentCategory === cat) && (
                                            <TableCell key={cat}>
                                                {c.categoryStatus?.[cat] ?? "-"}
                                            </TableCell>
                                        )
                                )}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </Box>

            <Typography sx={{ mt: 2 }}>
                Показано: {consumers.length}
            </Typography>
        </Container>
    );
}
