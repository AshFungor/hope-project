import { useNavigate } from 'react-router-dom';
import { useUser } from '@app/contexts/user';

const HomePage = () => {
    const navigate = useNavigate();
    const { currentUser } = useUser();

    const Button = (path: string, label: string) => (
        <button
            className="btn btn-outline-dark btn-lg mb-3"
            onClick={() => navigate(path)}
        >
            {label}
        </button>
    );

    return (
        <div className="container overflow-hidden">
            <div className="d-grid gap-2 d-mb-block mb-4">
                {Button('/personal/index', 'Личный кабинет')}
                {Button('/companies', 'Фирмы')}
                {Button('/prefecture', 'Префектура')}
                {Button('/city_hall', 'Мэрия')}
                {currentUser?.isAdmin && Button('/master', 'Мастер игры')}
            </div>
        </div>
    );
};

export default HomePage;
