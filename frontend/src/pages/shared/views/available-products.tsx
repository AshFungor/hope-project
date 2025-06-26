import { useEffect, useState } from 'react';
import { useUser } from '@app/contexts/user';
import { ProductAPI, AvailableProduct } from '@app/utils/product';
import ProductTable from '@app/pages/shared/widgets/product-table';

export default function AvailableProductsPage() {
	const { currentUser } = useUser();
	const [products, setProducts] = useState<AvailableProduct[]>([]);

	useEffect(() => {
		(async () => {
			if (!currentUser) return;

			try {
				const data = await ProductAPI.available(currentUser.bank_account_id);
				setProducts(data);
			} catch (err) {
				console.error('Failed to load products:', err);
			}
		})();
	}, [currentUser]);

	if (!currentUser) return null;

	return (
		<div className="container mt-4">
			<h2>Ваши продукты</h2>
			<ProductTable
				products={products}
				effectiveAccountId={currentUser.bank_account_id}
				showConsumeButton={true}
			/>
		</div>
	);
}
