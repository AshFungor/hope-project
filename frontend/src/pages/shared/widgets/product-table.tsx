import React from 'react';

import ProductRow from '@app/pages/shared/widgets/product-item';

import { ProductCountsResponse_ProductWithCount } from '@app/codegen/app/protos/products/count';
import { ConsumeProductResponse, ConsumeProductResponse_Status } from '@app/codegen/app/protos/products/consume'

interface ProductTableProperties {
	products: ProductCountsResponse_ProductWithCount[];
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
	products: ProductCountsResponse_ProductWithCount[];
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
					.filter((e) => e.product?.category === category)
					.map((e) => (
						<ProductRow
							key={e.product?.name}
							product={e}
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
	const categories = Array.from(new Set(products.map((p) => p.product?.category)));

	const visitConsumeResponse = (response: ConsumeProductResponse, bank_account_id: number, product: string) => {
		if (response.status == ConsumeProductResponse_Status.ALREADY_CONSUMED) {
			setMessage(`продукт ${product} уже употреблялся`)
		} else if (response.status == ConsumeProductResponse_Status.NOT_ENOUGH) {
			setMessage(`на аккаунте ${bank_account_id} не хватает продуктов для потребления`)
		} else if (response.status == ConsumeProductResponse_Status.OK)  {
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
						category={category ?? ''}
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
