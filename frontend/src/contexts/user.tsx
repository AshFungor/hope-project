import React, {
    createContext,
    useContext,
    useState,
    useEffect,
    useCallback,
    ReactNode,
} from "react";

import { User } from "@app/api/sub/session";
import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { UserRequest } from "@app/codegen/app/protos/session/user-info";
import { UserBankAccountIdProvider } from "@app/contexts/abstract/current-bank-account";

interface UserContextType {
    currentUser: User | null;
    setCurrentUser: (user: User | null) => void;
    refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProperties {
    children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProperties> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);

    const refreshUser = useCallback(async () => {
        try {
            const userRequest = UserRequest.create({});
            const response = await Hope.send(Request.create({ user: userRequest }));

            if (response?.user?.info) {
                const info = response.user.info;
                setCurrentUser(
                    new User(
                        info.name,
                        info.lastName,
                        info.patronymic,
                        info.login,
                        info.sex,
                        info.bonus,
                        info.birthday,
                        info.bankAccountId,
                        info.prefectureName,
                        info.isAdmin
                    )
                );
            } else {
                setCurrentUser(null);
            }
        } catch (err) {
            console.warn("Failed to refresh user:", err);
            setCurrentUser(null);
        }
    }, []);

    useEffect(() => {
        refreshUser();
    }, [refreshUser]);

    return (
        <UserContext.Provider value={{ currentUser, setCurrentUser, refreshUser }}>
            <UserBankAccountIdProvider id={currentUser?.bankAccountId}>
                {children}
            </UserBankAccountIdProvider>
        </UserContext.Provider>
    );
};

export const useUser = (): UserContextType => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within a UserProvider");
    }
    return context;
};
