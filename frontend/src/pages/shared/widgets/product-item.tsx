import React from 'react';
import { AvailableProduct } from '@app/utils/product';

interface ProductRowProperties {
	product: AvailableProduct;
	effectiveAccountId: number;
	getRowClass: (level: number) => string;
	showConsumeButton: boolean;
}

const ProductRow: React.FC<ProductRowProperties> = ({
	product,
	effectiveAccountId,
	getRowClass,
	showConsumeButton,
}) => {
	return (
		<tr className={getRowClass(product.level)}>
			<td>{product.name}</td>
			<td>{product.count}</td>
			<td>{product.level}</td>
			<td>
				{product.consumable && showConsumeButton && (
					<form
						action={`/api/product/consume?account=${effectiveAccountId}`}
						method="POST"
					>
						<input type="hidden" name="product" value={product.name} />
						<input type="hidden" name="account" value={effectiveAccountId} />
						<button type="submit" className="btn btn-success btn-sm">
							Потребить
						</button>
					</form>
				)}
			</td>
		</tr>
	);
};

export default ProductRow;
