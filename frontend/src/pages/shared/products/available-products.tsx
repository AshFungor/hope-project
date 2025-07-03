import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

import { useUser } from '@app/contexts/user';
import { PageMode } from '@app/types';

import MessageAlert, { AlertStatus } from '@app/widgets/shared/alert';

import { Hope } from '@app/api/api';
import { Request } from '@app/codegen/app/protos/request';

import {
	ProductCountsRequest,
	ProductCountsResponse_ProductWithCount,
} from '@app/codegen/app/protos/product/count';
import {
	ConsumeProductRequest,
	ConsumeProductResponse,
	ConsumeProductResponse_Status,
} from '@app/codegen/app/protos/product/consume';

const ProductRow: React.FC<{
	product: ProductCountsResponse_ProductWithCount;
	effectiveAccountId: number;
	onConsumed: (response: ConsumeProductResponse, bankAccountId: number, product: string) => void;
	showConsumeButton: boolean;
}> = ({ product, effectiveAccountId, onConsumed, showConsumeButton }) => {
	const getRowColor = (level: number): string => {
		switch (level) {
			case 1:
				return '#d1ecf1';
			case 2:
				return '#cce5ff';
			case 4:
				return '#fff3cd';
			default:
				return '#f8f9fa';
		}
	};

	const onConsumePressed = async () => {
		const request = ConsumeProductRequest.create({
			product: product.product?.name,
			bankAccountId: effectiveAccountId,
		});

		const response = await Hope.sendTyped(
			Request.create({ consumeProduct: request }),
			'consumeProduct'
		);

		onConsumed(response, effectiveAccountId, product.product?.name ?? '');
	};

	return (
		<TableRow sx={{ backgroundColor: getRowColor(product.product?.level ?? 0) }}>
			<TableCell>{product.product?.name}</TableCell>
			<TableCell>{product.count}</TableCell>
			<TableCell>{product.product?.level}</TableCell>
			<TableCell>
				{product.product?.consumable && showConsumeButton && (
					<Button
						size="small"
						variant="contained"
						color="success"
						onClick={onConsumePressed}
					>
						Потребить
					</Button>
				)}
			</TableCell>
		</TableRow>
	);
};

const ProductTable: React.FC<{
	products: ProductCountsResponse_ProductWithCount[];
	effectiveAccountId: number;
	showConsumeButton: boolean;
}> = ({ products, effectiveAccountId, showConsumeButton }) => {
	const [message, setMessage] = useState<{ contents: string; status: AlertStatus } | null>(null);

	const visitConsumeResponse = (
		response: ConsumeProductResponse,
		bankAccountId: number,
		product: string
	) => {
		switch (response.status) {
			case ConsumeProductResponse_Status.ALREADY_CONSUMED:
				setMessage({
					contents: `Продукт ${product} уже употреблялся`,
					status: AlertStatus.Warning,
				});
				break;
			case ConsumeProductResponse_Status.NOT_ENOUGH:
				setMessage({
					contents: `На аккаунте ${bankAccountId} не хватает продуктов для потребления`,
					status: AlertStatus.Error,
				});
				break;
			case ConsumeProductResponse_Status.OK:
				setMessage({
					contents: `Продукт ${product} успешно употреблён`,
					status: AlertStatus.Info,
				});
				break;
			default:
				setMessage({
					contents: `Неизвестный статус`,
					status: AlertStatus.Notice,
				});
		}
	};

	const categories = Array.from(new Set(products.map((p) => p.product?.category)));

	return (
		<>
			<MessageAlert
				message={message?.contents ?? null}
				status={message?.status ?? AlertStatus.Info}
			/>

			<Box sx={{ overflowX: 'auto', width: '100%', mt: 2 }}>
				<Table sx={{ minWidth: 600 }}>
					<TableHead>
						<TableRow>
							<TableCell>Название товара</TableCell>
							<TableCell>Количество</TableCell>
							<TableCell>Уровень</TableCell>
							<TableCell />
						</TableRow>
					</TableHead>

					{categories.map((category) => (
						<React.Fragment key={category ?? ''}>
							<TableHead>
								<TableRow>
									<TableCell colSpan={4}>
										<Typography variant="h6">{category}</Typography>
									</TableCell>
								</TableRow>
							</TableHead>
							<TableBody>
								{products
									.filter((p) => p.product?.category === category)
									.map((p) => (
										<ProductRow
											key={p.product?.name}
											product={p}
											effectiveAccountId={effectiveAccountId}
											onConsumed={visitConsumeResponse}
											showConsumeButton={showConsumeButton}
										/>
									))}
							</TableBody>
						</React.Fragment>
					))}
				</Table>
			</Box>
		</>
	);
};

interface AvailableProductsPageProps {
	mode: PageMode;
}

export default function AvailableProductsPage({ mode }: AvailableProductsPageProps) {
	const params = useParams();
	const { bankAccountId } = useUser();

	const effectiveAccountId = mode === 'company' ? Number(params.companyId) : bankAccountId;

	const [products, setProducts] = useState<ProductCountsResponse_ProductWithCount[]>([]);

	useEffect(() => {
		const fetchProducts = async () => {
			if (!effectiveAccountId) return;

			const countReq = ProductCountsRequest.create({ bankAccountId: effectiveAccountId });
			const response = await Hope.sendTyped(
				Request.create({ productCounts: countReq }),
				'productCounts'
			);

			setProducts(response.products);
		};

		fetchProducts();
	}, [effectiveAccountId]);

	if (!effectiveAccountId) {
		return null;
	}

	return (
		<Container sx={{ mt: 4 }}>
			<Typography variant="h4" gutterBottom>
				Ваши продукты
			</Typography>
			<ProductTable
				products={products}
				effectiveAccountId={effectiveAccountId}
				showConsumeButton={true}
			/>
		</Container>
	);
}
