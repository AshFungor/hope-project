import React, {
    createContext,
    useContext,
    useState,
    useEffect,
    useCallback,
    ReactNode,
} from "react";
import { useNavigate } from 'react-router-dom';

import { User } from "@app/api/sub/session";
import { Hope } from "@app/api/api";
import { Request } from "@app/codegen/app/protos/request";
import { UserRequest } from "@app/codegen/app/protos/session/user-info";

interface UserContextType {
    currentUser: User | null;
    bankAccountId: number | undefined;
    companyBankAccountId: number | undefined;
    effectiveId: number | undefined;
    setCurrentUser: (user: User | null) => void;
    refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProperties {
    children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProperties> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const navigate = useNavigate();

    const bankAccountId = currentUser?.bankAccountId;
    const companyBankAccountId = undefined; // TODO: hook up later
    const effectiveId = companyBankAccountId ?? bankAccountId;

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
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshUser();
    }, [refreshUser]);

    useEffect(() => {
        if (!isLoading && currentUser == null) {
            navigate("/auth/login");
        }
    }, [isLoading, currentUser, navigate]);

    return (
        <UserContext.Provider
            value={{
                currentUser,
                bankAccountId,
                companyBankAccountId,
                effectiveId,
                setCurrentUser,
                refreshUser,
            }}
        >
            {children}
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
