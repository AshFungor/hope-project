import React, { useEffect, useState } from 'react';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';

import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import Button from '@mui/material/Button';
import Autocomplete from '@mui/material/Autocomplete';

const MasterActionsPage: React.FC = () => {
    const [account, setAccount] = useState('');
    const [count, setCount] = useState('');
    const [productName, setProductName] = useState('');
    const [amount, setAmount] = useState('');
    const [products, setProducts] = useState<string[]>([]);

    useEffect(() => {
        (async () => {
            const response = await Hope.send(Request.create({ allProducts: {} }));
            const names = response.allProducts?.products?.map(p => p.name) ?? [];
            setProducts(names);
        })();
    }, []);

    const handleMoney = (formId: string) => {
        console.log(`Money form ${formId}:`, { account, count });
        // TODO: Send request to backend
    };

    const handleProduct = (formId: string) => {
        console.log(`Product form ${formId}:`, { account, productName, count, amount });
        // TODO: Send request to backend
    };

    const InputBlock = ({
        label,
        type,
        value,
        onChange,
    }: {
        label: string;
        type: string;
        value: string;
        onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    }) => (
        <TextField
            type={type}
            value={value}
            onChange={onChange}
            fullWidth
            InputProps={{
                startAdornment: <InputAdornment position="start">{label}</InputAdornment>,
            }}
            sx={{ mb: 3 }}
        />
    );

    return (
        <Box sx={{ maxWidth: 500, mx: 'auto', mt: 4 }}>
            <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    Списать надики
                </AccordionSummary>
                <AccordionDetails>
                    <InputBlock
                        label="Счет"
                        type="number"
                        value={account}
                        onChange={(e) => setAccount(e.target.value)}
                    />
                    <InputBlock
                        label="Количество"
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                    />
                    <Button
                        variant="contained"
                        color="success"
                        size="large"
                        fullWidth
                        onClick={() => handleMoney('1')}
                    >
                        Подтверждаю
                    </Button>
                </AccordionDetails>
            </Accordion>

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    Добавить надики
                </AccordionSummary>
                <AccordionDetails>
                    <InputBlock
                        label="Счет"
                        type="number"
                        value={account}
                        onChange={(e) => setAccount(e.target.value)}
                    />
                    <InputBlock
                        label="Количество"
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                    />
                    <Button
                        variant="contained"
                        color="success"
                        size="large"
                        fullWidth
                        onClick={() => handleMoney('2')}
                    >
                        Подтверждаю
                    </Button>
                </AccordionDetails>
            </Accordion>

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    Списать товар
                </AccordionSummary>
                <AccordionDetails>
                    <InputBlock
                        label="Счет"
                        type="number"
                        value={account}
                        onChange={(e) => setAccount(e.target.value)}
                    />

                    <Autocomplete
                        freeSolo
                        options={products}
                        value={productName}
                        onInputChange={(_, newValue) => setProductName(newValue)}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label="Название продукта"
                                fullWidth
                                sx={{ mb: 3 }}
                            />
                        )}
                    />

                    <InputBlock
                        label="Количество продукта"
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                    />

                    <InputBlock
                        label="Стоимость"
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                    />

                    <Button
                        variant="contained"
                        color="success"
                        size="large"
                        fullWidth
                        onClick={() => handleProduct('3')}
                    >
                        Подтверждаю
                    </Button>
                </AccordionDetails>
            </Accordion>

            <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    Добавить товар
                </AccordionSummary>
                <AccordionDetails>
                    <InputBlock
                        label="Счет"
                        type="number"
                        value={account}
                        onChange={(e) => setAccount(e.target.value)}
                    />

                    <Autocomplete
                        freeSolo
                        options={products}
                        value={productName}
                        onInputChange={(_, newValue) => setProductName(newValue)}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label="Название товара"
                                fullWidth
                                sx={{ mb: 3 }}
                            />
                        )}
                    />

                    <InputBlock
                        label="Количество"
                        type="number"
                        value={count}
                        onChange={(e) => setCount(e.target.value)}
                    />

                    <InputBlock
                        label="Стоимость"
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                    />

                    <Button
                        variant="contained"
                        color="success"
                        size="large"
                        fullWidth
                        onClick={() => handleProduct('4')}
                    >
                        Подтверждаю
                    </Button>
                </AccordionDetails>
            </Accordion>
        </Box>
    );
};

export default MasterActionsPage;
