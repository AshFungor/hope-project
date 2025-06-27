import { LoginRequest, LoginResponse, LoginResponse_LoginStatus } from "@app/codegen/session/login";
import { UserInfo } from "@app/codegen/session/user-info";
import { util } from "@app/utils/wrappers";

export namespace SessionAPI {
	export async function login(login: string, password: string): Promise<LoginResponse> {
		const requestMessage: LoginRequest = { login, password };
		const payload = LoginRequest.encode(requestMessage).finish();

		const response = await util.wrapApiCall(() =>
			fetch("/api/login", {
				method: "POST",
				headers: { "Content-Type": "application/protobuf" },
				credentials: "include",
				body: payload
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		return LoginResponse.decode(buffer);
	}

	export async function logout(): Promise<LoginResponse> {
		const response = await util.wrapApiCall(() =>
			fetch("/api/logout", {
				method: "POST",
				headers: { "Content-Type": "application/protobuf" },
				credentials: "include"
			})
		);

		const buffer = new Uint8Array(await response.arrayBuffer());
		return LoginResponse.decode(buffer);
	}

	export async function getCurrentUser(): Promise<UserInfo | null> {
		const response = await util.wrapApiCall(() =>
			fetch("/api/current_user", {
				method: "GET",
				headers: { "Accept": "application/protobuf" },
				credentials: "include"
			})
		);

		if (response.status === 401) {
			return null;
		}

		const buffer = new Uint8Array(await response.arrayBuffer());
		return UserInfo.decode(buffer);
	}
}
