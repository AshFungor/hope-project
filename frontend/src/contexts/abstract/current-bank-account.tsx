import React, { createContext, useContext, ReactNode } from "react";
import { useParams } from "react-router-dom";

export interface IdContextValue {
    id: number | undefined;
}

interface IdProviderProperties {
    children: ReactNode;
    id?: number;
}

export function createIdContext(
    fallback: () => number | undefined,
    paramKey: string,
    name: string
) {
    const IdContext = createContext<IdContextValue | undefined>(undefined);

    const Provider: React.FC<IdProviderProperties> = ({ children, id }) => {
        const params = useParams();
        const paramId = params[paramKey];
        const effectiveId =
            id !== undefined
                ? id
                : paramId !== undefined
                    ? Number(paramId)
                    : fallback();

        return (
            <IdContext.Provider value={{ id: effectiveId }}>
                {children}
            </IdContext.Provider>
        );
    };

    const useId = () => {
        const ctx = useContext(IdContext);
        if (!ctx) {
            throw new Error(`use${name} must be used within a ${name}Provider`);
        }
        return ctx;
    };

    return [Provider, useId] as const;
}

export const [UserBankAccountIdProvider, useUserBankAccountId] = createIdContext(
    () => undefined,
    "userBankAccountId",
    "UserBankAccountId"
);

export const [CompanyBankAccountIdProvider, useCompanyBankAccount] = createIdContext(
    () => undefined,
    "CompanyBankAccountId",
    "CompanyBankAccountId"
);

export interface EffectiveIdContextValue {
    id: number | undefined;
}

const EffectiveIdContext = createContext<EffectiveIdContextValue | undefined>(undefined);

export const EffectiveIdProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const { id: userBankAccountId } = useUserBankAccountId();
    const { id: companyBankAccountId } = useCompanyBankAccount();

    const effectiveId = companyBankAccountId ?? userBankAccountId;

    return (
        <EffectiveIdContext.Provider value={{ id: effectiveId }}>
            {children}
        </EffectiveIdContext.Provider>
    );
};

export const useEffectiveId = () => {
    const ctx = useContext(EffectiveIdContext);
    if (!ctx) {
        throw new Error("useEffectiveId must be used within EffectiveIdProvider");
    }
    return ctx;
};

