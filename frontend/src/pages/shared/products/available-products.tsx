import React, { useEffect, useState } from "react";

import { useParams } from "react-router-dom";
import { useUser } from "@app/contexts/user";
import { PageMode } from "@app/types"

import MessageAlert, { AlertStatus } from "@app/widgets/shared/alert";

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";

import {
    ProductCountsRequest,
    ProductCountsResponse_ProductWithCount,
} from "@app/codegen/app/protos/products/count";
import {
    ConsumeProductRequest,
    ConsumeProductResponse,
    ConsumeProductResponse_Status,
} from "@app/codegen/app/protos/products/consume";


const ProductRow: React.FC<{
    product: ProductCountsResponse_ProductWithCount;
    effectiveAccountId: number;
    onConsumed: (response: ConsumeProductResponse, bankAccountId: number, product: string) => void;
    showConsumeButton: boolean;
}> = ({ product, effectiveAccountId, onConsumed, showConsumeButton }) => {
    const getRowClass = (level: number): string => {
        switch (level) {
            case 1:
                return 'table-info';
            case 2:
                return 'table-primary';
            case 4:
                return 'table-warning';
            default:
                return 'table-light';
        }
    };

    const onConsumePressed = async () => {
        const request = ConsumeProductRequest.create({
            product: product.product?.name,
            account: effectiveAccountId,
        });

        const response = await Hope.sendTyped(
            Request.create({ consumeProduct: request }),
            "consumeProduct"
        );

        onConsumed(response, effectiveAccountId, product.product?.name ?? '');
    };

    return (
        <tr className={getRowClass(product.product?.level ?? 0)}>
            <td>{product.product?.name}</td>
            <td>{product.count}</td>
            <td>{product.product?.level}</td>
            <td>
                {product.product?.consumable && showConsumeButton && (
                    <button className="btn btn-success btn-sm" onClick={onConsumePressed}>
                        Потребить
                    </button>
                )}
            </td>
        </tr>
    );
};


const ProductTable: React.FC<{
    products: ProductCountsResponse_ProductWithCount[];
    effectiveAccountId: number;
    showConsumeButton: boolean;
}> = ({ products, effectiveAccountId, showConsumeButton }) => {
    const [message, setMessage] = useState<{contents: string, status: AlertStatus} | null>(null);

    const visitConsumeResponse = (
        response: ConsumeProductResponse,
        bankAccountId: number,
        product: string
    ) => {
        switch (response.status) {
            case ConsumeProductResponse_Status.ALREADY_CONSUMED:
                setMessage({
                    contents: `Продукт ${product} уже употреблялся`,
                    status: AlertStatus.Warning
                });
                break;
            case ConsumeProductResponse_Status.NOT_ENOUGH:
                setMessage({
                    contents: `На аккаунте ${bankAccountId} не хватает продуктов для потребления`,
                    status: AlertStatus.Error
                });
                break;
            case ConsumeProductResponse_Status.OK:
                setMessage({
                    contents: `Продукт ${product} успешно употреблён`,
                    status: AlertStatus.Info
                });
                break;
            default:
                setMessage({
                    contents: `Неизвестный статус`,
                    status: AlertStatus.Notice
                });
        }
    };

    const categories = Array.from(new Set(products.map((p) => p.product?.category)));
    return (
        <>
            <MessageAlert
				message={message?.contents ?? null}
				status={AlertStatus.Info}
			/>

            <table className="table">
                <thead>
                    <tr>
                        <th>Название товара</th>
                        <th>Количество</th>
                        <th>Уровень</th>
                        <th></th>
                    </tr>
                </thead>

                {categories.map((category) => (
                    <React.Fragment key={category ?? ''}>
                        <thead>
                            <tr>
                                <th colSpan={4}>{category}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products
                                .filter((p) => p.product?.category === category)
                                .map((p) => (
                                    <ProductRow
                                        key={p.product?.name}
                                        product={p}
                                        effectiveAccountId={effectiveAccountId}
                                        onConsumed={visitConsumeResponse}
                                        showConsumeButton={showConsumeButton}
                                    />
                                ))}
                        </tbody>
                    </React.Fragment>
                ))}
            </table>
        </>
    );
};


interface AvailableProductsPageProps {
    mode: PageMode;
}


export default function AvailableProductsPage({ mode }: AvailableProductsPageProps) {
    const params = useParams();
    const { bankAccountId } = useUser();

    const effectiveAccountId =
        mode === 'company'
            ? Number(params.companyId)
            : bankAccountId;

    const [products, setProducts] = useState<ProductCountsResponse_ProductWithCount[]>([]);

    useEffect(() => {
        const fetchProducts = async () => {
            if (!effectiveAccountId) return;

            const countReq = ProductCountsRequest.create({ bankAccountId: effectiveAccountId });
            const response = await Hope.sendTyped(
                Request.create({ productCounts: countReq }),
                "productCounts"
            );

            setProducts(response.products);
        };

        fetchProducts();
    }, [effectiveAccountId]);

    if (!effectiveAccountId) {
        return null;
    }

    return (
        <div className="container mt-4">
            <h2>Ваши продукты</h2>
            <ProductTable
                products={products}
                effectiveAccountId={effectiveAccountId}
                showConsumeButton={true}
            />
        </div>
    );
}
