import React from 'react';

interface BalanceSectionProperties {
	current: number;
}

const BalanceSection: React.FC<BalanceSectionProperties> = ({ current }) => {
	return (
		<div className="mb-4">
			<p className="mb-1">
				<strong>Ваш баланс:</strong> {current}
			</p>
		</div>
	);
};

export default BalanceSection;
