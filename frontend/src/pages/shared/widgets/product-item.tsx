import React from 'react';

import { Hope } from "@app/api/api";

import { ProductCountsResponse_ProductWithCount } from '@app/codegen/app/protos/products/count';
import { ConsumeProductRequest, ConsumeProductResponse } from '@app/codegen/app/protos/products/consume';
import { Request } from '@app/codegen/app/protos/request';

interface ProductRowProperties {
	product: ProductCountsResponse_ProductWithCount;
	effectiveAccountId: number;
	getRowClass: (level: number) => string;
	onConsumed: (response: ConsumeProductResponse, bank_account_id: number, product: string) => void;
	showConsumeButton: boolean;
}

const ProductRow: React.FC<ProductRowProperties> = ({
	product,
	effectiveAccountId,
	getRowClass,
	onConsumed,
	showConsumeButton,
}) => {
	const onConsumePressed = async (bank_account_id: number, product: string) => {
		const request = ConsumeProductRequest.create({ product: product, account: bank_account_id })
		let response = await Hope.send(Request.create({ consumeProduct: request }))

		if (!response.consumeProduct) {
			throw Error("failed to consume: request failed")
		}

		onConsumed(response.consumeProduct, bank_account_id, product)
	}

	return (
		<tr className={getRowClass(product.product?.level ?? 0)}>
			<td>{product.product?.name}</td>
			<td>{product.count}</td>
			<td>{product.product?.level}</td>
			<td>
				{product.product?.consumable && showConsumeButton && (
					<button
						className="btn btn-success btn-sm"
						onClick={() => {
							onConsumePressed(effectiveAccountId, product.product?.name ?? '')
						}}
					>
						Потребить
					</button>
				)}
			</td>
		</tr>
	);
};

export default ProductRow;
