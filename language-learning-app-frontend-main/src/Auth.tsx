import { useState } from 'react';
import { useLoginUserApiLoginPost } from './api/users/users';
import { useAuth } from './api/ApiConfigContext';
import { useLocation, useNavigate } from 'react-router-dom';

export default function Auth() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const { setToken, setRoles } = useAuth();
    const { mutate, status, error, data } = useLoginUserApiLoginPost();
    const isLoading = status === 'pending';
    const isError = status === 'error';
    const location = useLocation();
    const navigate = useNavigate();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        mutate(
            { data: { email, password } },
            {
                onSuccess: (response) => {
                    const data = response?.data as { access_token?: string; token?: string; roles?: string[] };
                    const token = data?.access_token || data?.token || null;
                    const roles = data?.roles || [];
                    if (token) {
                        setToken(token);
                        setRoles(roles);
                        const redirectTo = (location.state as any)?.from?.pathname || '/reference';
                        navigate(redirectTo, { replace: true });
                    }
                },
            }
        );
    };

    return (
        <form onSubmit={handleSubmit} style={{ maxWidth: 320, margin: '2rem auto', display: 'flex', flexDirection: 'column', gap: 12 }}>
            <h2>Login</h2>
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
            />
            <button type="submit" disabled={isLoading}>Login</button>
            {isError && <div style={{ color: 'red' }}>Error: {error?.message}</div>}
            {data && <div style={{ color: 'green' }}>Login successful!</div>}
        </form>
    );
}
