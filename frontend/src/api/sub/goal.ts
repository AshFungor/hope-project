import { Request } from "@app/codegen/app/protos/request";
import { Protobuf } from "@app/api/request";

import { Goal as GoalType } from "@app/codegen/app/protos/types/goal";

export class Goal implements GoalType {
    constructor(
        public bankAccountId: number,
        public value: number,
    ) {}

    getRate(currentBalance: number): number {
        if (!this.value || this.value === 0) {
            return 0;
        }
        return Math.min(100, Math.floor((currentBalance / this.value) * 100));
    }
}

export namespace API {
    export namespace Goal {

        export async function handle(request: Request) {
            if (request.createGoal) {
                return Protobuf.send("/api/goal/create", request, "POST");
            }

            if (request.lastGoal) {
                return Protobuf.send("/api/goal/get_last", request, "POST");
            }

            throw new Error("Unsupported Goal payload type");
        }
    }
}
