import { createContext, useContext, useState, useEffect, useCallback } from "react";

import { User } from "@app/api/sub/session";
import { Hope } from "@app/api/api";

import { Request } from "@app/codegen/app/protos/request";
import { UserRequest } from "@app/codegen/app/protos/session/user-info";

interface UserContextType {
    currentUser: User | null;
    setCurrentUser: (user: User | null) => void;
    refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);

    const refreshUser = useCallback(async () => {
        try {
            const userRequest = UserRequest.create({});
            const response = (
                await Hope.send(Request.create({ user: userRequest }))
            );

            setCurrentUser(
                response?.user?.info
                  ? new User(
                      response.user?.info.name,
                      response.user?.info.lastName,
                      response.user?.info.patronymic,
                      response.user?.info.login,
                      response.user?.info.sex,
                      response.user?.info.bonus,
                      response.user?.info.birthday,
                      response.user?.info.bankAccountId,
                      response.user?.info.prefectureName,
                      response.user?.info.isAdmin
                    )
                  : null
            );

        } catch (err) {
            setCurrentUser(null);
            console.warn("Failed to refresh user:", err);
        }
    }, []);

    useEffect(() => {
        refreshUser();
    }, [refreshUser]);

    return (
        <UserContext.Provider value={{ currentUser, setCurrentUser, refreshUser }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => {
    const context = useContext(UserContext);
    if (!context) throw new Error("useUser must be used within a UserProvider");
    return context;
};
