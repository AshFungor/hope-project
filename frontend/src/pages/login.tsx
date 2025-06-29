import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useUser } from "@app/contexts/user";
import { AlertStatus, MessageAlert } from "@app/widgets/shared/alert"

import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { LoginRequest, LoginResponse_LoginStatus } from "@app/codegen/app/protos/session/login";

export default function LoginPage() {
    const [login, setLogin] = useState("");
    const [password, setPassword] = useState("");
    const [error, setMessage] = useState("");

    const navigate = useNavigate();
    const { refreshUser } = useUser();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage("");

        try {
            const loginRequest = LoginRequest.create({ login, password });
            const response = await Hope.send(Request.create({ login: loginRequest }));

            if (response.login?.status !== LoginResponse_LoginStatus.OK) {
                setMessage("Введен неправильный логин или пароль");
            } else {
                await refreshUser();
                navigate("/");
            }
        } catch (err) {
            setMessage("Ошибка подключения к серверу");
        }
    };

    return (
        <main className="form-signin">
            <form onSubmit={handleSubmit}>
                <h1 className="h3 mb-3 fw-normal text-center">
                    Пожалуйста, войдите
                </h1>

                <MessageAlert message={error}/>

                <div className="form-floating mb-3">
                    <input
                        type="text"
                        className="form-control"
                        id="floatingInput"
                        placeholder="Login"
                        value={login}
                        onChange={(e) => setLogin(e.target.value)}
                        required
                    />
                    <label htmlFor="floatingInput">Логин</label>
                </div>

                <div className="form-floating mb-3">
                    <input
                        type="password"
                        className="form-control"
                        id="floatingPassword"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <label htmlFor="floatingPassword">Пароль</label>
                </div>

                <button className="w-100 btn btn-lg btn-primary" type="submit">
                    Войти
                </button>
            </form>
        </main>
    );
}
