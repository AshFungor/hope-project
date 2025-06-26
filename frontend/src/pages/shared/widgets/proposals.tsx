import React from 'react';
import { Link } from 'react-router-dom';

interface ProposalLinksProperties {
    accountId?: number;
	showTransfer?: boolean;
	showInvoice?: boolean;
	showUnpaid?: boolean;
	showHistory?: boolean;
}

const ProposalLinks: React.FC<ProposalLinksProperties> = ({
    accountId,
	showTransfer = true,
	showInvoice = true,
	showUnpaid = true,
	showHistory = true,
}) => {
	return (
		<>
			{showTransfer && (
				<Link className="btn btn-outline-dark btn-lg mb-3" to={`/proposal/money/${accountId}`}>
					Перевод
				</Link>
			)}
			{showInvoice && (
				<Link className="btn btn-outline-dark btn-lg mb-3" to="/proposal/bill">
					Выставить счет
				</Link>
			)}
			{showUnpaid && (
				<Link className="btn btn-outline-dark btn-lg mb-3" to={`/proposal/unpaid/${accountId}`}>
					Неоплаченные счета
				</Link>
			)}
			{showHistory && (
				<Link className="btn btn-outline-dark btn-lg mb-3" to={`/proposal/history/${accountId}`}>
					История транзакций
				</Link>
			)}
		</>
	);
};

export default ProposalLinks;
