import React from 'react';

import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

interface BalanceSectionProperties {
	current: number;
}

const BalanceSection: React.FC<BalanceSectionProperties> = ({ current }) => {
	return (
		<Box
			className="text-center mb-3 rounded balance-blur"
			sx={{
				textAlign: 'center',
				mb: 3,
				borderRadius: 1,
			}}
			style={
				{
					'--balance': `${current}`,
					'--percentage': `${Math.min(current / 10, 100)}%`,
				} as React.CSSProperties
			}
		>
			<Typography variant="body1">
				<strong>Баланс:</strong> {current} Ψ
			</Typography>
		</Box>
	);
};

export default BalanceSection;
