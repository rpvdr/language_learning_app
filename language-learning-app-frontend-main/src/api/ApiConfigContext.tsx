import axios from 'axios';
import React, { createContext, useContext, useState, useMemo } from 'react';

axios.defaults.baseURL = process.env.NODE_ENV === 'development' 
    ? 'http://127.0.0.1:8000'
    : '';

axios.defaults.headers.common['ngrok-skip-browser-warning'] = '1'

export type AuthContextType = {
    token: string | null;
    setToken: (token: string | null) => void;
    roles: string[];
    setRoles: (roles: string[]) => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const getInitialToken = () => sessionStorage.getItem('authToken');
    const getInitialRoles = () => {
        const raw = sessionStorage.getItem('authRoles');
        return raw ? JSON.parse(raw) : [];
    };
    const [_, setIgnored] = useState(0); // dummy state to force re-render

    const setToken = (token: string | null) => {
        if (token) {
            sessionStorage.setItem('authToken', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            sessionStorage.removeItem('authToken');
            delete axios.defaults.headers.common['Authorization'];
        }
        setIgnored(i => i + 1); // force re-render
    };

    const setRoles = (roles: string[]) => {
        sessionStorage.setItem('authRoles', JSON.stringify(roles));
        setIgnored(i => i + 1); // force re-render
    };

    const token = getInitialToken();
    const roles = getInitialRoles();
    if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete axios.defaults.headers.common['Authorization'];
    }
    const value = useMemo(() => ({ token, setToken, roles, setRoles }), [token, roles]);

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
};
