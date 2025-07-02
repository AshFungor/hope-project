import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

export namespace API {
    export namespace CityHall {
        export async function handle(request: Request) {
            if (request.cityHall) {
                return Protobuf.send("/api/city_hall", request, "POST");
            }

            throw new Error("Unsupported CityHall payload type");
        }
    }
}
