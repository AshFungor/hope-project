export class Product {
	constructor(
		public name: string,
		public category: string,
		public level: number
	) {}

	static async getAllProducts(): Promise<Array<Product>> {
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

	static async getProductCount(bank_account_id: number, product_name: string): Promise<number> {
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

	static async getAvailableProductNames(bank_account_id: number): Promise<Array<string>> {
		const params = new URLSearchParams({
			bank_account_id: bank_account_id.toString(),
		});
		const response = await fetch(`/api/products/names?${params.toString()}`, {
			credentials: 'include',
		});

		let text = await response.text();
		return JSON.parse(text).names;
	}

	static async getAvailableProducts(bank_account_id: number): Promise<Array<[Product, number]>> {
		const availableNames = await this.getAvailableProductNames(bank_account_id);
		const allProducts = await this.getAllProducts();

		const result: Array<[Product, number]> = [];

		for (const name of availableNames) {
			const product = allProducts.find((p) => p.name === name);
			if (!product) continue;

			const count = await this.getProductCount(bank_account_id, name);
			result.push([product, count]);
		}

		return result;
	}
}
