import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace User {
        export async function handle(request: Request) {
            if (request.fullUser) {
                return Protobuf.send("/api/user/current_user", request, "POST");
            }

            if (request.partialUser) {
                return Protobuf.send("/api/user/partial_user", request, "POST");
            }

            throw new Error("Unsupported Session payload type");
        }
    }
}
