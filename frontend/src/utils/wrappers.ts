import { StatusCodes } from 'http-status-codes';

export namespace util {

    async function internal(response: Response) {
        let text = await response.text()
        console.error(`request failed: internal error: ${text}`)
    }

    async function notFound(response: Response) {
        let text = await response.text()
        console.error(`request failed: url was not found: ${text}`)
    }

    export async function wrapApiCall(call: (...parameters: any[]) => Promise<Response>, ...parameters: any[]) {
        let response = await call(parameters)

        switch (response.status) {
            case StatusCodes.INTERNAL_SERVER_ERROR:
                internal(response)
            case StatusCodes.NOT_FOUND:
                notFound(response)
        }

        return response
    }

}