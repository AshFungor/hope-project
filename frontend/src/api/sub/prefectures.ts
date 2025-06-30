import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace Prefectures {
        export async function handle(request: Request) {
            if (request.allPrefectures) {
                return Protobuf.send("/api/prefecture/all", request, "POST");
            }

            if (request.updatePrefectureLink) {
                return Protobuf.send("/api/prefecture/link/update", request, "POST");
            }

            throw new Error("Unsupported Prefecture request type");
        }
    }
}
