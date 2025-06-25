import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Auth } from '@app/utils/auth';
import { CurrentUser } from '@app/types/user';

interface UserContextType {
	currentUser: CurrentUser | null;
	setCurrentUser: (user: CurrentUser | null) => void;
	refreshUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);

	const refreshUser = useCallback(async () => {
		try {
			const user = await Auth.fetchCurrentUser();
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
