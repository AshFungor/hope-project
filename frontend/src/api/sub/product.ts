import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace Product {
        export async function handle(request: Request) {
            if (request.allProducts) {
                return Protobuf.send("/api/products/all", request, "POST");
            }

            if (request.availableProducts) {
                return Protobuf.send("/api/products/available", request, "POST");
            }

            if (request.consumeProduct) {
                return Protobuf.send("/api/products/consume", request, "POST");
            }

            if (request.productCounts) {
                return Protobuf.send("/api/products/counts", request, "POST");
            }

            if (request.createProduct) {
                return Protobuf.send("/api/products/create", request, "POST");
            }

            throw new Error("Unsupported Product payload type");
        }
    }
}
