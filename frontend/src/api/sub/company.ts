import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace Company {
        export async function handle(request: Request) {
            if (request.createCompany) {
                return Protobuf.send("/api/company/create", request, "POST");
            }

            if (request.allCompanies) {
                return Protobuf.send("/api/companies/all", request, "POST");
            }

            if (request.getCompany) {
                return Protobuf.send("/api/company/get", request, "POST");
            }

            if (request.allEmployees) {
                return Protobuf.send("/api/company/employees", request, "POST");
            }

            if (request.employ) {
                return Protobuf.send("/api/company/employ", request, "POST");
            }

            if (request.fire) {
                return Protobuf.send("/api/company/fire", request, "POST");
            }

            throw new Error("Unsupported Company payload type");
        }
    }
}
