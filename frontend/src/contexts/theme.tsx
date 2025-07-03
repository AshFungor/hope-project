import React, { createContext, useMemo, useState, useContext, ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme, CssBaseline } from '@mui/material';

type ThemeMode = 'light' | 'dark';

interface ThemeContextValue {
	mode: ThemeMode;
	toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export const useThemeMode = () => {
	const context = useContext(ThemeContext);
	if (!context) {
		throw new Error('useThemeMode must be used within a ThemeProvider');
	}
	return context;
};

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
	const [mode, setMode] = useState<ThemeMode>('light');

	const toggleTheme = () => {
		setMode((prev) => (prev === 'light' ? 'dark' : 'light'));
	};

	const theme = createTheme({
		palette: {
			mode: 'light',
			primary: {
				main: '#9a5500',
			},
			secondary: {
				main: '#f50057',
			},
		},
	});

	return (
		<ThemeContext.Provider value={{ mode, toggleTheme }}>
			<MuiThemeProvider theme={theme}>
				<CssBaseline />
				{children}
			</MuiThemeProvider>
		</ThemeContext.Provider>
	);
};
