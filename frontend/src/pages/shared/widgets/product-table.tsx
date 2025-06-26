import React from 'react';

import { types } from '@app/types/product';
import { StatusCodes } from 'http-status-codes';
import { ConsumeProductResponse, ConsumeProductResponse_Status } from '@app/codegen/products/consume'

import ProductRow from '@app/pages/shared/widgets/product-item';

interface ProductTableProperties {
	products: types.AvailableProduct[];
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
	products: types.AvailableProduct[];
	effectiveAccountId: number;
	showConsumeButton: boolean;
	onConsume: (response: ConsumeProductResponse, bank_account_id: number, product: string) => void;
}> = ({ category, products, effectiveAccountId, showConsumeButton, onConsume }) => {
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
							onConsumed={onConsume}
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
	const [message, setMessage] = React.useState<string | null>(null);
	const categories = Array.from(new Set(products.map((p) => p.category)));

	const visitConsumeResponse = (response: ConsumeProductResponse, bank_account_id: number, product: string) => {
		if (response.status == ConsumeProductResponse_Status.ALREADY_CONSUMED) {
			setMessage(`продукт ${product} уже употреблялся`)
		} else if (response.status == ConsumeProductResponse_Status.NOT_ACCEPTABLE) {
			setMessage(`на аккаунте ${bank_account_id} не хватает продуктов для потребления`)
		} else if (response.status == ConsumeProductResponse_Status.SUCCESS)  {
			setMessage(`продукт ${product} успешно употреблен`)
		}
	}

	return (
		<>
			{message && (
				<div className="alert alert-success text-center" role="alert">
					{message}
				</div>
			)}
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
						onConsume={visitConsumeResponse}
					/>
				))}
			</table>
		</>
	);
};

export default ProductTable;
