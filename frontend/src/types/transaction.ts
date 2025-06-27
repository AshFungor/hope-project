import { util } from '@app/utils/wrappers';
import {
    CreateMoneyTransactionRequest,
    CreateProductTransactionRequest,
} from '@app/codegen/transaction/create';
import {
    ViewHistoryRequest,
    ViewTransactionsResponse,
    TransactionEntry_Status,
    TransactionEntry,
} from '@app/codegen/transaction/history';
import {
    DecideTransactionRequest,
} from '@app/codegen/transaction/transaction';
import {
    ViewCurrentTransactionsRequest,
    CurrentTransactionsResponse,
    CurrentTransactionEntry,
} from '@app/codegen/transaction/unpaid';

export namespace TransactionAPI {
    export interface TransactionRecord {
        transaction_id: number;
        product: string;
        count: number;
        amount: number;
        status: 'created' | 'approved' | 'rejected' | 'completed';
        updated_at: string;
        side: 'seller' | 'customer';
        second_side: number;
        is_money: boolean;
    }

    function convertStatus(status: TransactionEntry_Status): TransactionRecord['status'] {
        switch (status) {
            case TransactionEntry_Status.CREATED:
                return 'created';
            case TransactionEntry_Status.APPROVED:
                return 'approved';
            case TransactionEntry_Status.REJECTED:
                return 'rejected';
            case TransactionEntry_Status.COMPLETED:
                return 'completed';
            default:
                return 'created';
        }
    }

    export async function createProductProposal(
        seller_account: number,
        customer_account: number,
        product: string,
        count: number,
        amount: number
    ): Promise<Response> {
        const req = CreateProductTransactionRequest.create({
            seller_account,
            customer_account,
            product,
            count,
            amount,
        });

        const encoded = CreateProductTransactionRequest.encode(req).finish();
        return util.wrapApiCall(() =>
            fetch('/api/transaction/product/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/octet-stream' },
                credentials: 'include',
                body: encoded,
            })
        );
    }

    export async function createMoneyProposal(
        seller_account: number,
        customer_account: number,
        amount: number
    ): Promise<Response> {
        const req = CreateMoneyTransactionRequest.create({
            seller_account,
            customer_account,
            amount,
        });

        const encoded = CreateMoneyTransactionRequest.encode(req).finish();
        return util.wrapApiCall(() =>
            fetch('/api/transaction/money/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/octet-stream' },
                credentials: 'include',
                body: encoded,
            })
        );
    }

    export async function getActiveProposals(account: number): Promise<TransactionRecord[]> {
        const req = ViewCurrentTransactionsRequest.create({ account });
        const encoded = ViewCurrentTransactionsRequest.encode(req).finish();

        const response = await util.wrapApiCall(() =>
            fetch('/api/transaction/view/current', {
                method: 'POST',
                headers: { 'Content-Type': 'application/octet-stream' },
                credentials: 'include',
                body: encoded,
            })
        );

        const buffer = new Uint8Array(await response.arrayBuffer());
        const decoded = CurrentTransactionsResponse.decode(buffer);

        return decoded.transactions.map((entry: CurrentTransactionEntry) => ({
            transaction_id: entry.transactionId,
            product: entry.product,
            count: entry.count,
            amount: entry.amount,
            status: 'created',
            updated_at: '',
            side: 'customer',
            second_side: entry.secondSide,
            is_money: false,
        }));
    }

    export async function getTransactionHistory(account: number): Promise<TransactionRecord[]> {
        const req = ViewHistoryRequest.create({ account });
        const encoded = ViewHistoryRequest.encode(req).finish();

        const response = await util.wrapApiCall(() =>
            fetch('/api/transaction/view/history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/octet-stream' },
                credentials: 'include',
                body: encoded,
            })
        );

        const buffer = new Uint8Array(await response.arrayBuffer());
        const decoded = ViewTransactionsResponse.decode(buffer);

        return decoded.transactions.map((entry) => ({
            transaction_id: entry.transactionId,
            product: entry.product,
            count: entry.count,
            amount: entry.amount,
            status: convertStatus(entry.status),
            updated_at: entry.updatedAt,
            side: entry.side as 'seller' | 'customer',
            second_side: entry.secondSide,
            is_money: entry.isMoney,
        }));
    }

    export async function decideOnProposal(
        transaction_id: number,
        status: 'approved' | 'rejected'
    ): Promise<Response> {
        const req = DecideTransactionRequest.create({
            account: transaction_id,
            status,
        });

        const encoded = DecideTransactionRequest.encode(req).finish();
        return util.wrapApiCall(() =>
            fetch('/api/transaction/decide', {
                method: 'POST',
                headers: { 'Content-Type': 'application/octet-stream' },
                credentials: 'include',
                body: encoded,
            })
        );
    }
}
