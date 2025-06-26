import { createContext, useContext, useState, useEffect, useCallback } from 'react';

import { SessionAPI } from '@app/types/user';
import { UserInfo } from '@app/codegen/session/user-info';

interface UserContextType {
	currentUser: UserInfo | null;
	setCurrentUser: (user: UserInfo | null) => void;
	refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [currentUser, setCurrentUser] = useState<UserInfo | null>(null);

	const refreshUser = useCallback(async () => {
		try {
			const user = await SessionAPI.getCurrentUser();
			setCurrentUser(user);
		} catch (err) {
			setCurrentUser(null);
			console.warn('Failed to refresh user:', err);
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
	if (!context) throw new Error('useUser must be used within a UserProvider');
	return context;
};
