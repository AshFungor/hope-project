import 'bootstrap/dist/css/bootstrap.min.css';
import '@app/styles/main.css';

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from '@app/app';

ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<App />
	</React.StrictMode>
);
