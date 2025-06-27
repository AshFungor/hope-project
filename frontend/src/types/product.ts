import { ConsumeProductRequest, ConsumeProductResponse, ConsumeProductResponse_Status as ConsumeStatus } from '@app/codegen/products/consume';
import { ProductListResponse, ConsumableCategoriesResponse } from '@app/codegen/products/all';
import { ProductCountRequest, ProductCountResponse } from '@app/codegen/products/count';
import { ProductNamesRequest, ProductNamesResponse} from '@app/codegen/products/names';

import { util } from '@app/utils/wrappers';

export namespace types {
	export class Product {
		constructor(
			public name: string,
			public category: string,
			public level: number
		) {}
	}

	export class AvailableProduct extends Product {
		constructor(
			name: string,
			category: string,
			level: number,
			public count: number,
			public consumable: boolean
		) {
			super(name, category, level);
		}
	}
}

export namespace ProductAPI {
	export async function all(): Promise<Array<types.Product>> {
		const response = await util.wrapApiCall(() =>
			fetch('/api/products/all', {
				method: 'GET',
				headers: { Accept: 'application/protobuf' },
				credentials: 'include'
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = ProductListResponse.decode(buffer);

		return parsed.products.map(
			(p) => new types.Product(p.name, p.category, p.level)
		);
	}

	export async function count(bank_account_id: number, product_name: string): Promise<number> {
		const req = ProductCountRequest.create({ bank_account_id, product_name });

		const response = await util.wrapApiCall(() =>
			fetch('/api/products/count', {
				method: 'POST',
				headers: { 'Content-Type': 'application/protobuf' },
				credentials: 'include',
				body: ProductCountRequest.encode(req).finish()
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = ProductCountResponse.decode(buffer);

		return parsed.count;
	}

	export async function availableNames(bank_account_id: number): Promise<string[]> {
		const req = ProductNamesRequest.create({ bank_account_id });

		const response = await util.wrapApiCall(() =>
			fetch('/api/products/names', {
				method: 'POST',
				headers: { 'Content-Type': 'application/protobuf' },
				credentials: 'include',
				body: ProductNamesRequest.encode(req).finish()
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = ProductNamesResponse.decode(buffer);

		return parsed.names;
	}

	export async function consumableCategories(): Promise<string[]> {
		const response = await util.wrapApiCall(() =>
			fetch('/api/products/consumable', {
				method: 'GET',
				headers: { Accept: 'application/protobuf' },
				credentials: 'include'
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		const parsed = ConsumableCategoriesResponse.decode(buffer);

		return parsed.consumables;
	}

	export async function available(bank_account_id: number): Promise<Array<types.AvailableProduct>> {
		const [names, products, consumables] = await Promise.all([
			availableNames(bank_account_id),
			all(),
			consumableCategories()
		]);

		const result: Array<types.AvailableProduct> = [];

		for (const name of names) {
			const product = products.find((p) => p.name === name);
			if (!product) continue;

			const countVal = await count(bank_account_id, name);
			const isConsumable = consumables.includes(product.category);

			result.push(
				new types.AvailableProduct(
					product.name,
					product.category,
					product.level,
					countVal,
					isConsumable
				)
			);
		}

		return result;
	}

	export async function consume(bank_account_id: number, product_name: string): Promise<ConsumeProductResponse> {
		const req = ConsumeProductRequest.create({
			account: bank_account_id,
			product: product_name
		});

		const response = await util.wrapApiCall(() =>
			fetch('/api/products/consume', {
				method: 'POST',
				headers: { 'Content-Type': 'application/protobuf' },
				credentials: 'include',
				body: ConsumeProductRequest.encode(req).finish()
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		return ConsumeProductResponse.decode(buffer);
	}
}
