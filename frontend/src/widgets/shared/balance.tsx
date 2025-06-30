import React from 'react';

interface BalanceSectionProperties {
	current: number;
}

const BalanceSection: React.FC<BalanceSectionProperties> = ({ current }) => {
	return (
		<div className="text-center mb-3 rounded balance-blur"
			style={{
				'--balance': `${current}`,
				'--percentage': `${Math.min(current / 10, 100)}%`
			} as React.CSSProperties}>
			<span><strong>Баланс:</strong> {current} Ψ</span>
		</div>
	);
};

export default BalanceSection;
