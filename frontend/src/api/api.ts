import { Request } from "@app/codegen/app/protos/request";
import { Response } from "@app/codegen/app/protos/response";

import { API as SessionAPI } from "@app/api/sub/session";
import { API as ProductAPI } from "@app/api/sub/product";
import { API as TransactionAPI } from "@app/api/sub/transaction";
import { API as GoalAPI } from "@app/api/sub/goal";
import { API as PrefectureAPI } from "@app/api/sub/prefecture";
import { API as CompanyAPI } from "@app/api/sub/company";

export namespace Hope {
    export async function send(request: Request): Promise<Response> {
        let response: Response;

        if (request.login || request.user || request.logout) {
            response = await SessionAPI.Session.handle(request);

        } else if (request.allPrefectures || request.updatePrefectureLink) {
            response = await PrefectureAPI.Prefecture.handle(request);

        } else if (request.createCompany) {
            response = await CompanyAPI.Company.handle(request);

        } else if (
            request.allProducts ||
            request.availableProducts ||
            request.consumeProduct ||
            request.productCounts ||
            request.createProduct
        ) {
            response = await ProductAPI.Product.handle(request);

        } else if (
            request.createProductTransaction ||
            request.createMoneyTransaction ||
            request.decideOnTransaction ||
            request.viewTransactionHistory ||
            request.currentTransactions
        ) {
            response = await TransactionAPI.Transaction.handle(request);

        } else if (request.createGoal || request.lastGoal) {
            response = await GoalAPI.Goal.handle(request);

        } else {
            throw new Error(`Unsupported request: none of the oneof fields set`);
        }

        return response;
    }

    export async function sendTyped<K extends keyof Response>(
        request: Request,
        field: K
    ): Promise<NonNullable<Response[K]>> {
        const response = await send(request);
        const data = response[field];

        if (!data) {
            throw new Error(`Expected Response to contain '${field}' but got: ${JSON.stringify(response)}`);
        }

        return data;
    }
}
