import React, { useEffect, useState } from "react";
import { Accordion, Form, Button, InputGroup } from "react-bootstrap";
import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";

const MasterActionsPage: React.FC = () => {
    const [account, setAccount] = useState("");
    const [count, setCount] = useState("");
    const [productName, setProductName] = useState("");
    const [amount, setAmount] = useState("");
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

    return (
        <Accordion defaultActiveKey="0">
            <Accordion.Item eventKey="1">
                <Accordion.Header>Списать надики</Accordion.Header>
                <Accordion.Body>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Счет</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={account}
                            onChange={(e) => setAccount(e.target.value)}
                        />
                    </InputGroup>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Количество</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={count}
                            onChange={(e) => setCount(e.target.value)}
                        />
                    </InputGroup>
                    <Button size="lg" variant="success" onClick={() => handleMoney("1")}>
                        Подтверждаю
                    </Button>
                </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="2">
                <Accordion.Header>Добавить надики</Accordion.Header>
                <Accordion.Body>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Счет</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={account}
                            onChange={(e) => setAccount(e.target.value)}
                        />
                    </InputGroup>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Количество</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={count}
                            onChange={(e) => setCount(e.target.value)}
                        />
                    </InputGroup>
                    <Button size="lg" variant="success" onClick={() => handleMoney("2")}>
                        Подтверждаю
                    </Button>
                </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="5">
                <Accordion.Header>Списать товар</Accordion.Header>
                <Accordion.Body>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Счет</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={account}
                            onChange={(e) => setAccount(e.target.value)}
                        />
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Название продукта</InputGroup.Text>
                        <Form.Control
                            type="text"
                            list="product-list"
                            value={productName}
                            onChange={(e) => setProductName(e.target.value)}
                        />
                        <datalist id="product-list">
                            {products.map((p) => (
                                <option key={p} value={p} />
                            ))}
                        </datalist>
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Количество продукта</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={count}
                            onChange={(e) => setCount(e.target.value)}
                        />
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Стоимость</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                        />
                    </InputGroup>

                    <Button size="lg" variant="success" onClick={() => handleProduct("3")}>
                        Подтверждаю
                    </Button>
                </Accordion.Body>
            </Accordion.Item>

            <Accordion.Item eventKey="6">
                <Accordion.Header>Добавить товар</Accordion.Header>
                <Accordion.Body>
                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Счет</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={account}
                            onChange={(e) => setAccount(e.target.value)}
                        />
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Название товара</InputGroup.Text>
                        <Form.Control
                            type="text"
                            list="product-list"
                            value={productName}
                            onChange={(e) => setProductName(e.target.value)}
                        />
                        <datalist id="product-list">
                            {products.map((p) => (
                                <option key={p} value={p} />
                            ))}
                        </datalist>
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Количество</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={count}
                            onChange={(e) => setCount(e.target.value)}
                        />
                    </InputGroup>

                    <InputGroup className="mb-4 input-group-lg">
                        <InputGroup.Text>Стоимость</InputGroup.Text>
                        <Form.Control
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                        />
                    </InputGroup>

                    <Button size="lg" variant="success" onClick={() => handleProduct("4")}>
                        Подтверждаю
                    </Button>
                </Accordion.Body>
            </Accordion.Item>
        </Accordion>
    );
};

export default MasterActionsPage;
