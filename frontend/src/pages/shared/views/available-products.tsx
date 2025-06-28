import { useEffect, useState } from 'react';
import { useUser } from '@app/contexts/user';

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { ProductCountsRequest, ProductCountsResponse_ProductWithCount } from '@app/codegen/app/protos/products/count';

import ProductTable from '@app/pages/shared/widgets/product-table';

export default function AvailableProductsPage() {
	const { currentUser } = useUser();
	const [products, setProducts] = useState<ProductCountsResponse_ProductWithCount[]>([]);

	useEffect(() => {
		(async () => {
			if (!currentUser) return;

			const countReq = ProductCountsRequest.create({
				bankAccountId: currentUser.bankAccountId
			});
			const countResponse = await Hope.send(
				Request.create({ productCounts: countReq })
			);

			// should move to separate context
			const counts = countResponse?.productCounts?.products ?? null
			if (counts === null) {
				throw Error("failed to fetch products: could not complete request")
			}

			setProducts(counts);
		})();
	}, [currentUser]);

	if (!currentUser) return null;

	return (
		<div className="container mt-4">
			<h2>Ваши продукты</h2>
			<ProductTable
				products={products}
				effectiveAccountId={currentUser.bankAccountId}
				showConsumeButton={true}
			/>
		</div>
	);
}
