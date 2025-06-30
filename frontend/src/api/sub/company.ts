import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace Company {
        export async function handle(request: Request) {
            if (request.createCompany) {
                return Protobuf.send("/api/company/create", request, "POST");
            }
            throw new Error("Unsupported Company payload type");
        }
    }
}
