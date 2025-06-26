import React from 'react';
import { AvailableProduct } from '@app/utils/product';
import ProductRow from '@app/pages/shared/widgets/product-item';

interface ProductTableProperties {
	products: AvailableProduct[];
	effectiveAccountId: number;
	showConsumeButton: boolean;
}

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

const ProductCategorySection: React.FC<{
	category: string;
	products: AvailableProduct[];
	effectiveAccountId: number;
	showConsumeButton: boolean;
}> = ({ category, products, effectiveAccountId, showConsumeButton }) => {
	return (
		<React.Fragment key={category}>
			<thead>
				<tr>
					<th colSpan={4}>{category}</th>
				</tr>
			</thead>
			<tbody>
				{products
					.filter((p) => p.category === category)
					.map((product) => (
						<ProductRow
							key={product.name}
							product={product}
							effectiveAccountId={effectiveAccountId}
							getRowClass={getRowClass}
							showConsumeButton={showConsumeButton}
						/>
					))}
			</tbody>
		</React.Fragment>
	);
};

const ProductTable: React.FC<ProductTableProperties> = ({
	products,
	effectiveAccountId,
	showConsumeButton,
}) => {
	const categories = Array.from(new Set(products.map((p) => p.category)));

	return (
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
				<ProductCategorySection
					key={category}
					category={category}
					products={products}
					effectiveAccountId={effectiveAccountId}
					showConsumeButton={showConsumeButton}
				/>
			))}
		</table>
	);
};

export default ProductTable;
