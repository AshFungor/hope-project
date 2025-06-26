import React from 'react';
import { AvailableProduct, ProductAPI } from '@app/utils/product';

interface ProductRowProperties {
	product: AvailableProduct;
	effectiveAccountId: number;
	getRowClass: (level: number) => string;
	onConsumed: (response: Response, bank_account_id: number, product: string) => void;
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
		let response = await ProductAPI.consume(bank_account_id, product)
		onConsumed(response, bank_account_id, product)
	}

	return (
		<tr className={getRowClass(product.level)}>
			<td>{product.name}</td>
			<td>{product.count}</td>
			<td>{product.level}</td>
			<td>
				{product.consumable && showConsumeButton && (
					<button
						className="btn btn-success btn-sm"
						onClick={() => {
							onConsumePressed(effectiveAccountId, product.name)
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
