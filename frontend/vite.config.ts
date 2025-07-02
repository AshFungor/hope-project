import { defineConfig, type UserConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

const CONFIG = {
	development: {
		API_URL: 'http://localhost',
	},
	production: {
		// life is hard
		API_URL: 'http://192.168.200.200',
	},
} as const;

export default defineConfig(({ command }): UserConfig => {
	const isDev = command === 'serve';
	const config = isDev ? CONFIG.development : CONFIG.production;

	return {
		plugins: [react()],
		server: isDev
			? {
				proxy: {
					'/api': {
						target: config.API_URL,
						changeOrigin: true,
						secure: false,
					},
				},
			}
			: undefined,
		build: !isDev
			? {
				outDir: 'dist',
				sourcemap: false,
			}
			: undefined,
		define: {
			__API_URL__: JSON.stringify(config.API_URL),
		},
		resolve: {
			alias: {
				'@app': path.resolve(__dirname, 'src'),
			},
		},
	};
});
