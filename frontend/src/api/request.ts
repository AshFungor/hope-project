import axios, { AxiosResponse, Method } from "axios";

import { Request } from "@app/codegen/app/protos/request";
import { Response } from "@app/codegen/app/protos/response";

export namespace Protobuf {
    export async function send(
        url: string,
        request: Request,
        method: Method = "GET"
    ): Promise<Response> {
        const axiosResponse = await axios.request<ArrayBuffer>({
            url,
            method,
            data: Request.encode(request).finish(),
            responseType: "arraybuffer",
            withCredentials: true,
            headers: {
                "Content-Type": "application/protobuf",
                "Accept": "application/protobuf"
            }
        });

        return receive(axiosResponse);
    }

    export function receive(
        axiosResponse: AxiosResponse<ArrayBuffer>
    ): Response {
        return Response.decode(new Uint8Array(axiosResponse.data));
    }
}
