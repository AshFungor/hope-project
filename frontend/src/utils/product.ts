export class Product {
	constructor(
		public name: string,
		public category: string,
		public level: number
	) {}
}

export class AvailableProduct extends Product {
	constructor(
		public name: string,
		public category: string,
		public level: number,
		public count: number,
		public consumable: boolean
	) {
		super(name, category, level);
	}
}

export class ProductAPI {
	static async all(): Promise<Array<Product>> {
		const response = await fetch('/api/products/all');

		if (!response.ok) {
			throw Error(`failed to fetch products: ${response.text()}`);
		}

		const text = await response.text();
		let products: Array<Product> = [];
		for (const product of JSON.parse(text)) {
			products.push(new Product(product.name, product.category, product.level));
		}
		return products;
	}

	static async counts(bank_account_id: number, product_name: string): Promise<number> {
		const params = new URLSearchParams({
			bank_account_id: bank_account_id.toString(),
			product_name: product_name,
		});
		const response = await fetch(`/api/products/count?${params.toString()}`, {
			credentials: 'include',
		});

		let text = await response.text();
		return JSON.parse(text).count;
	}

	static async availableNames(bank_account_id: number): Promise<Array<string>> {
		const params = new URLSearchParams({
			bank_account_id: bank_account_id.toString(),
		});
		const response = await fetch(`/api/products/names?${params.toString()}`, {
			credentials: 'include',
		});

		let text = await response.text();
		return JSON.parse(text).names;
	}

	static async consumableCategories(): Promise<Array<string>> {
		const response = await fetch('/api/products/consumable');

		if (!response.ok) {
			throw Error(`failed to fetch consumable categories: ${response.text()}`);
		}

		const text = await response.text();
		return JSON.parse(text).consumables;
	}

	static async available(bank_account_id: number): Promise<Array<AvailableProduct>> {
		const [availableNames, allProducts, consumableCategories] = await Promise.all([
			this.availableNames(bank_account_id),
			this.all(),
			this.consumableCategories(),
		]);

		const result: AvailableProduct[] = [];

		for (const name of availableNames) {
			const product = allProducts.find((p) => p.name === name);
			if (!product) continue;

			const count = await this.counts(bank_account_id, name);
			const consumable = consumableCategories.includes(product.category);

			result.push(
				new AvailableProduct(
					product.name,
					product.category,
					product.level,
					count,
					consumable
				)
			);
		}

		return result;
	}

	static async consume(bank_account_id: number, product_name: string): Promise<Response> {
		const response = await fetch('/api/products/consume', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			credentials: 'include',
			body: JSON.stringify({
				product: product_name,
				account: bank_account_id,
			}),
		});

		return response
	}	
}
